## 1. Install Chocolatey (Window)

- Follows the instruction in this website.

    [Chocolatey Installation](https://chocolatey.org/install)

## 2. Install Mkcert

For Mac and Linux.
```
brew install mkcert
```
For Window.
```
choco install mkcert
```

## 3. Generate a Local Certificate

- Run the following commands in your project directory

```
mkcert -install
mkcert 127.0.0.1 localhost
```

## 4. Create certs directory

- create a directory named "certs" in your project directory.
- moves "127.0.0.1+1-key.pem", "127.0.0.1+1.pem" into certs directory. 