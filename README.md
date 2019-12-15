# API RESTful: URL-Shortener
Projeto que cria uma APIRESTful para encurtar URLs
# Dependências
Pacotes para Ubuntu, utilize o install.sh

* `apt-get update`
* `apt-get install python3`
* `apt-get install python3-pip`
* `pip3 install flask`
* `pip3 install markdown`
* `pip3 install dataset`
* `apt-get install postgresql`
* `pip3 install psycopg2-binary`

Para conectar ao banco de dados, se foi utilizado o usuário padrão `postgres`, foi preciso atualizar a senha deste, já que a conexão exige uma autenticação. Também é necessário criar uma `database`.
Faça:

* `sudo -u postgres -i`
* `psql`
* `postgres=# ALTER USER postgres PASSWORD 'postgres';`
* `postgres=# CREATE DATABASE mydatabase`
* `postgres=# \q`
* `exit `

# Como usar
A API é baseada em métodos HTTP que permitem que requisições sejam feitas, sendo elas:

### GET /urls/:id
Redireciona a sua url para a url original.
Retorna `301 Redirect` em caso de redirecionamento e `404 Not Found` caso a url não exista.

### POST /users
Cria um usuário, conforme o padrão abaixo retornando `201 Created`.

`{"id": "jibao"}`
### POST /users/:userid/urls
Cadastra uma nova url no sistema de padrão json como exemplificado abaixo:

`{"url": "http://www.chaordic.com.br/folks"}`

Retorna `201 Created`.

### GET /stats
Retorna estatísticas globais do sistema, como o número total de acessos, de urls cadastradas e as 10 urls mais acessadas.

### GET /users/:userId/stats
Retorna estatísticas das urls de um usuário. O resultado é o mesmo que `GET /stats` mas com o escopo dentro de um usuário.
Caso o usuário não exista, retorna `404 Not Found`.

### GET /stats/:id
Retorna estatísticas de uma url específica: Sua id, o número de hits, sua url original e sua url encurtada.

### DELETE /urls/:id
Deleta uma url do sistema.

### DELETE /user/:userId
Apaga um usuário.



