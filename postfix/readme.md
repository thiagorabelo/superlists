# Configuração do Postfix em máquina virtual

Este tutorial axilia na criação do [Postfix](http://www.postfix.org/) em uma
máquina virtual para que seja possível dar continuidade as estudos sem que seja
necessário usar alguma solução de terceiros.

    Atenção! De forma alguma utilize este tutorial para criar seu próprio
    servidor de emails. Este tutorial arranha apenas a superfície do assunto e
    tem como propósito apenas por uma instância do Postfix em execução sem se
    preocupar com todos os detalhes de segurança ou performance.

## Instalando o Postfix

Vamos passar a variável de ambiente `DEBIAN_PRIORITY=low` para nosso comando de
instalação para forçá-lo a responder a alguns prompts adicionais:

```sh
sudo DEBIAN_PRIORITY=low apt install postfix
```

O assistente de instalação fará algumas perguntas, sendo elas (dependendo da
instalação, essas perguntas podem aparecer em inglês):

- **Tipo geral de de configuração de email**: Para esta iremos escolher **Site
da internet**, já que esta corresponde às nossas necessidades de infraestrutura.

- **Nome de email do sistema**: Este é o domínio base usado para construir um
endereço de email válido quando apenas a parte da conta é fornecida. Por
exemplo, o nome do host do nosso servidor é `mail.thomas.com`, mas
provavelmente queremos definir o nome do correio do sistema como `thomas.com`
para que, dado o nome de usuário `user1`, o Postfix use o endereço
`user1@thomas.com`.

- **Destinatário das mensagens para root e postmaster**: Esta é a conta Linux em
que serão encaminhados e-mails destinados a `root@` e `postmaster@`. Use sua
conta principal para isso. No nosso caso, `sammy`.

- **Outros destinos para os quais deve aceitar mensagens**: Define os destinos
de e-mail que essa instância do Postfix aceitará. Se precisar adicionar
quaisquer outros domínios que este servidor será responsável por receber,
adicione-os aqui. Caso contrário, o padrão deve funcionar bem.

- **Forçar atualizações síncronas na fila de mensagens?**: Uma vez que você
provavelmente está usando um sistema de arquivos com _journal_, aceite a opção
**No** aqui.

- **Redes locais**: Esta é uma lista das redes para as quais seu servidor de
e-mail está configurado para retransmitir as mensagens. A rede padrão deve
funcionar para a maioria dos cenários. Se escolher modificá-la, certifique-se
de ser bastante restritivo em relação ao alcance da rede.

- **Limite de tamanho da caixa postal**: Isso pode ser usado para limitar o
tamanho das mensagens. Definindo-o para "0" desativa qualquer restrição de
tamanho.

- **Caractere de extensão de endereço local**: Este é o caractere que pode ser
usado para separar a parte regular do endereço de uma extensão (usado para criar
pseudônimos dinâmicos).

- **Protocolos de Internet para usar**: Escolha se vai restringir a versão de IP
que o Postfix suporta. Vamos escolher "_todos_" para nossos fins.

Esta são as configurações que usaremos neste tutorial:

- **Tipo geral de de configuração de email**: Internet Site
- **Nome de email do sistema**: thomas.com (não mail.example.com)
- **Destinatário das mensagens para root e postmaster**: sammy
- **Outros destinos para os quais deve aceitar mensagens**: $myhostname,
  thomas.com, mail.thomas.com, localhost.thomas.com e localhost
- **Forçar atualizações síncronas na fila de mensagens?**: No
- **Redes locais**: 127.0.0.0/8[ ::ffff:127.0.0.0]/104[ ::1]/128
- **Limite de tamanho da caixa postal**: 0
- **Caractere de extensão de endereço local**: +
- **Protocolos de Internet para usar**: todos

## Pacotes

Nossa instância do Postfix usará o banco de dados [Postgres](https://www.postgresql.org/)
como _backend_ para armazenar os usuários do serviço de email. Portando devemos
instalar os pacotes necessários:

```sh
sudo apt install postgresql postfix-pgsql
```

Instale também o [Dovecot](https://www.dovecot.org/), um servidor de
[IMAP](https://en.wikipedia.org/wiki/Internet_Message_Access_Protocol) e
[POP3](https://en.wikipedia.org/wiki/Post_Office_Protocol) open source para
sistemas Linux e UNIX.

```sh
sudo apt install dovecot-lmtpd dovecot-pgsql dovecot-imapd dovecot-pop3d
```

## Configuração do banco de dados Postgres

Ajuste isso para as suas necessidades, se você já possui uma configuração do
postgres em execução! Mas, a partir de uma nova instalação do postgres, vamos
configurar a autenticação para que possamos fornecer acesso ao dovecot ao banco
de dados. Adicione o seguinte ao `/etc/postgresql/10/main/pg_ident.conf`:

```pg_ident.conf
mailmap         dovecot                 mailreader
mailmap         postfix                 mailreader
mailmap         root                    mailreader
```

E o seguinte para `/etc/postgresql/10/main/pg_hba.conf` (Alerta: certifique-se
de adicioná-lo logo após o bloco de comentários _Put your actual configuration here_!
Caso contrário, uma das entradas padrão poderá pegar primeiro e a autenticação
do banco de dados falhará.)

```pg_hba.conf
local       mail    all     peer map=mailmap
```

Em seguida, recarregue o postgresql (`sudo systemctl restart postgresql.service`).
Agora configure o banco de dados:

```sh
$ sudo -u postgres psql
postgres=# CREATE USER mailreader;
postgres=# REVOKE CREATE ON SCHEMA public FROM PUBLIC;
postgres=# REVOKE USAGE ON SCHEMA public FROM PUBLIC;
postgres=# GRANT CREATE ON SCHEMA public TO postgres;
postgres=# GRANT USAGE ON SCHEMA public TO postgres;
postgres=# CREATE DATABASE mail WITH OWNER mailreader;
postgres=# \q

$ sudo psql -U mailreader -d mail
postgres=# \c mail

mail=# CREATE TABLE aliases (
    alias text NOT NULL,
    email text NOT NULL
);
mail=# CREATE TABLE users (
    email text NOT NULL,
    password text NOT NULL,
    maildir text NOT NULL,
    created timestamp with time zone DEFAULT now()
);
mail=# ALTER TABLE aliases OWNER TO mailreader;
mail=# ALTER TABLE users OWNER TO mailreader;
mail=# \q
```

Você pode adicionar caixas de correio virtuais como esta, a partir do shell:

```sh
$ sudo doveadm pw -s sha512 -r 100
Enter new password: ...
Retype new password: ...
{SHA512}.............................................................==

$ sudo psql -U mailreader -d mail
mail=# INSERT INTO users (
    email,
    password,
    maildir
) VALUES (
    'foo@thomas.com',
    '{SHA512}.............................................................==',
    'foo/'
);
```

## Instalação do Dovecot

Precisamos conectar o dovecot ao banco de dados e configurar o servidor LMTP.
Configure um novo usuário (o dovecot se recusará a lidar com emails sem um
usuário do sistema configurado para ele) e o diretório para os emails
primeiro (você pode usar `/var/mail`, mas que tradicionalmente usa o formato
mbox, enquanto usaremos o formato maildir superior):

```sh
$ sudo adduser --system --no-create-home --uid 500 --group \
               --disabled-password --disabled-login \
               --gecos 'dovecot virtual mail user' vmail
$ sudo mkdir /home/mailboxes
$ sudo chown vmail:vmail /home/mailboxes
$ sudo chmod 700 /home/mailboxes
```

Agora salve a seguinte configuração como `/etc/dovecot/dovecot-sql.conf`

```dovecot-sql.conf
driver = pgsql
connect = host=/var/run/postgresql/ dbname=mail user=mailreader
default_pass_scheme = SHA512
password_query = SELECT email as user, password FROM users WHERE email = '%u'
user_query = SELECT email as user, 'maildir:/home/mailboxes/maildir/' || maildir as mail, '/home/mailboxes/home/'||maildir as home, 500 as uid, 500 as gid FROM users WHERE email = '%u'
```

Certifique-se que este arquivo pertence ao `root` e mude as permissões para 600.

Agora abra `/etc/dovecot/dovecot.conf` e edite as configurações de `passdb` e
`userdb` para ficar assim:

```dovecot.conf
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
```

Continuando no mesmo arquivo, mude a sub-rotina de protocolos para:

```dovecot.conf
protocols = imap lmtp pop3
```

E finalmente, ainda no mesmo arquivo:

```dovecot.conf
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
```

## Postfix

Agora precisamos informar ao postfix para entregar as mensagens diretamente para
o dovecot. Abra `/etc/postfix/main.cf` e adicione:

```main.cf
mailbox_transport = lmtp:unix:private/dovecot-lmtp
```

ao fim. Agora precisamos definir a configuração do banco de dados para o postfix.

Crie o arquivo `/etc/postfix/pgsql-aliases.cf` e digite:

```pgsql-aliases.cf
user=mailreader
dbname=mail
table=aliases
select_field=alias
where_field=email
hosts=unix:/var/run/postgresql
```

Em seguida, crie o arquivo `/etc/postfix/pgsql-boxes.cf` e digite:

```pgsql-boxes.cf
user=mailreader
dbname=mail
table=users
select_field=email
where_field=email
hosts=unix:/var/run/postgresql/
```

Agora altere a linha `alias_maps` em `main.cf` para ler o arquivo
`pgsql-aliases.cf`:

```main.cf
alias_maps = hash:/etc/aliases proxy:pgsql:/etc/postfix/pgsql-aliases.cf
```

e a linha `local_recipient_maps` para ler o arquivo `pgsql-boxes.cf`:

```main.cf
local_recipient_maps = proxy:pgsql:/etc/postfix/pgsql-boxes.cf $alias_maps
```

e adicione sua rede local na configuração `mynetworks` para que o Postfix
aceite conexões a partir de sua rede, por exemplo:

```main.cf
mynetworks = 127.0.0.0/8 [::ffff:127.0.0.0]/104 [::1]/128 192.168.1.0/24
```

Adicione os nomes que você escolheu no arquivo `/etc/hosts`, tanto na máquina
virtual onde está instalado o Postfix, quanto na máquina onde serão executados
os testes. Na máquina virtual:

```hosts
127.0.0.1       mail.thomas.com pop.thomas.com thomas.com
```

e na máquina onde serão executados os testes:

```hosts
192.168.1.5       mail.thomas.com pop.thomas.com thomas.com
```

## Terminando

Agora basta recarregar:

```sh
$ postfix reload
$ service dovecot restart
```
