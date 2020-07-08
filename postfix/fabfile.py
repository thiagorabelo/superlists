 # pylint: disable=line-too-long

"""
$ sudo apt install debconf-utils
$ sudo debconf-get-selections | grep postfix
postfix postfix/lmtp_retired_warning    boolean true
postfix postfix/destinations    string  $myhostname, thomas.com, email.thomas.com, thomas, localhost.localdomain, localhost
postfix postfix/relay_restrictions_warning      boolean
postfix postfix/dynamicmaps_conversion_warning  boolean
postfix postfix/sqlite_warning  boolean
postfix postfix/mydomain_warning        boolean
postfix postfix/kernel_version_warning  boolean
postfix postfix/relayhost       string
postfix postfix/newaliases      boolean false
postfix postfix/recipient_delim string  +
postfix postfix/not_configured  error
postfix postfix/mailbox_limit   string  0
postfix postfix/protocols       select  all
postfix postfix/mynetworks      string  127.0.0.0/8 [::ffff:127.0.0.0]/104 [::1]/128
postfix postfix/procmail        boolean false
postfix postfix/mailname        string  thomas.com
postfix postfix/chattr  boolean false
postfix postfix/compat_conversion_warning       boolean true
postfix postfix/main_mailer_type        select  Internet Site
postfix postfix/root_address    string  thiago
postfix postfix/rfc1035_violation       boolean false
postfix postfix/retry_upgrade_warning   boolean
postfix postfix/main_cf_conversion_warning      boolean true
postfix postfix/tlsmgr_upgrade_warning  boolean
postfix postfix/bad_recipient_delimiter error
"""


from fabric.contrib.files import append, sed
from fabric.api import run, sudo


# TODO: Fazer script aceitar parâmetros


CONFIGURATION = {
    "postfix postfix/main_mailer_type select": "Internet Site",
    "postfix postfix/mailname string": "thomas.com",
    "postfix postfix/root_address string": "thiago",

    # TODO: Tem um bug no debconf que não consegue usar esta configuração.
    #       Vai ter que alterar essa configuração diretamente em
    #       /etc/postfix/main.cf.
    "postfix postfix/destinations string": "$myhostname, thomas.com, thomas, "
                                           "localhost.localdomain, localhost, "
                                           "mail.thomas.com",
    "postfix postfix/chattr boolean": "false",
    "postfix postfix/mynetworks string": "127.0.0.0/8 [::ffff:127.0.0.0]/104 "
                                         "[::1]/128 192.168.100.0/24",
    "postfix postfix/mailbox_limit string": "0",
    "postfix postfix/recipient_delim string": "+",
    "postfix postfix/protocols select": "all"
}


def _fix_destinations(hostname):
    expected_destination = f"$myhostname, {hostname}.com, mail.{hostname}.com, {hostname}, " \
                           "localhost.localdomain, localhost"
    mydestination = run("""grep "mydestination = " /etc/postfix/main.cf"""
                        """ | sed -e 's/mydestination = //g'""")

    if not mydestination == expected_destination:
        sed("/etc/postfix/main.cf",
            "mydestination = .+$",
            f"mydestination = {expected_destination}",
            use_sudo=True)


def _get_pg_version():
    pg_version = run("apt-cache show postgresql | grep Depends:"
                     " | sed 's/Depends: postgresql-//g' | head -n 1")
    return pg_version


def install_postfix():
    commands = " && ".join(f"""( echo {key} {val} | debconf-set-selections )"""
                           for key, val in CONFIGURATION.items())
    sudo(f"{commands} && DEBIAN_FRONTEND=noninteractive apt-get install -qqy postfix")
    _fix_destinations("thomas")


def install_pg():
    sudo("apt-get install -qqy postgresql postfix-pgsql")


def config_pg():
    pg_version = _get_pg_version()
    pg_ident_path = f" /etc/postgresql/{pg_version}/main/pg_ident.conf"
    sudo(
        f"cat <<EOF>> {pg_ident_path}\n"
        "mailmap         dovecot                 mailreader\n"
        "mailmap         postfix                 mailreader\n"
        "mailmap         root                    mailreader\n"
        "EOF\n",
        user="postgres"
    )

    pg_hba_path = f"/etc/postgresql/{pg_version}/main/pg_hba.conf"
    search = "# ----------------------------------"
    new_conf = "local       mail    all     peer map=mailmap"
    tmp_file = "/tmp/new.txt"
    sudo(
        f"sed 's/{search}/{search}\\n\\n{new_conf}\\n/g' \"{pg_hba_path}\" > \"{tmp_file}\" "
        f"&& cp \"{tmp_file}\" \"{pg_hba_path}\" "
        f"&& rm \"{tmp_file}\"",
        user="postgres"
    )

    sudo("systemctl restart postgresql.service")

    sudo(
        'psql -c "CREATE USER mailreader;"'
        '&& psql -c "REVOKE CREATE ON SCHEMA public FROM PUBLIC;"'
        '&& psql -c "REVOKE USAGE ON SCHEMA public FROM PUBLIC;"'
        '&& psql -c "GRANT CREATE ON SCHEMA public TO postgres;"'
        '&& psql -c "GRANT USAGE ON SCHEMA public TO postgres;"'
        '&& psql -c "CREATE DATABASE mail WITH OWNER mailreader;"',
        user="postgres"
    )
    sudo(
        'psql -U mailreader -d mail -c "CREATE TABLE aliases ( alias text NOT NULL, '
        'email text NOT NULL );"'

        '&& psql -U mailreader -d mail -c "CREATE TABLE users ( email text NOT NULL, '
        'password text NOT NULL, maildir text NOT NULL, '
        'created timestamp with time zone DEFAULT now() );"'

        '&& psql -U mailreader -d mail -c "ALTER TABLE aliases OWNER TO mailreader;"'
        '&& psql -U mailreader -d mail -c "ALTER TABLE users OWNER TO mailreader;"'
    )

def install_dovecot():
    run("sudo apt-get install -qqy dovecot-lmtpd dovecot-pgsql dovecot-imapd dovecot-pop3d")


def config_dovecot(local_network, etc_hosts):
    user = "vmail"
    user_home = "/home/mailboxes"

    sudo("adduser --system --no-create-home --uid 500 --group --disabled-password "
         f"--disabled-login --gecos 'Dovecot virtual mail user' {user}")
    sudo(f"mkdir -p {user_home}")
    sudo(f"chown {user}:{user} {user_home}")

    append(
        "/etc/dovecot/dovecot-sql.conf",
        """driver = pgsql
connect = host=/var/run/postgresql/ dbname=mail user=mailreader
default_pass_scheme = SHA512
password_query = SELECT email as user, password FROM users WHERE email = '%u'
user_query = SELECT email as user, 'maildir:/home/mailboxes/maildir/' || maildir as mail, '/home/mailboxes/home/'||maildir as home, 500 as uid, 500 as gid FROM users WHERE email = '%u'
""", use_sudo=True)
    sudo("chown root:root /etc/dovecot/dovecot-sql.conf")
    sudo("chmod 600 /etc/dovecot/dovecot-sql.conf")

    append(
        "/tmp/part.txt",
        """

passdb {
    driver = sql
    args = /etc/dovecot/dovecot-sql.conf
}

userdb {
    driver = prefetch
}

# The userdb below is used only by lda.
userdb {
    driver = sql
    args = /etc/dovecot/dovecot-sql.conf
}

protocols = imap lmtp pop3

service lmtp {
  unix_listener /var/spool/postfix/private/dovecot-lmtp {
    group = postfix
    mode = 0600
    user = postfix
  }
}

protocol lmtp {
  postmaster_address=postmaster@thomas.org
  hostname=mail.thomas.org
}

""",
        use_sudo=True
    )

    sudo("cat /tmp/part.txt >> /etc/dovecot/dovecot.conf")
    sudo("rm /tmp/part.txt")

    append(
        "/tmp/part.txt",
        "\n\nmailbox_transport = lmtp:unix:private/dovecot-lmtp\n",
        use_sudo=True
    )
    sudo("cat /tmp/part.txt >> /etc/postfix/main.cf")
    sudo("rm /tmp/part.txt")

    append(
        "/etc/postfix/pgsql-aliases.cf",
        """user=mailreader
dbname=mail
table=aliases
select_field=alias
where_field=email
hosts=unix:/var/run/postgresql
""",
        use_sudo=True
    )

    append(
        "/etc/postfix/pgsql-boxes.cf",
        """user=mailreader
dbname=mail
table=users
select_field=email
where_field=email
hosts=unix:/var/run/postgresql/
""",
        use_sudo=True
    )

    sed(
        "/etc/postfix/main.cf",
        r"(alias_maps\s*=\s*.+$)",
        r"\1 proxy:pgsql:/etc/postfix/pgsql-aliases.cf\n"
        r"local_recipient_maps = proxy:pgsql:/etc/postfix/pgsql-boxes.cf $alias_maps",
        use_sudo=True
    )
    sed(
        "/etc/postfix/main.cf",
        r"(mynetworks\s*=\s*.+$)",
        f"\\1 {local_network}",
        use_sudo=True
    )

    sed(
        "/etc/hosts",
        r"(127\.0\.0\.1\s+localhost)",
        f"\\1 {etc_hosts}",
        use_sudo=True
    )


def restart_services():
    sudo("postfix reload")
    sudo("sudo systemctl restart postfix.service")
    sudo("sudo systemctl restart dovecot.service")


def deploy():
    install_postfix()
    install_pg()
    config_pg()

    install_dovecot()
    config_dovecot(local_network='192.168.100.0/24',
                   etc_hosts='mail.thomas.com pop.thomas.com thomas.com')

    restart_services()
