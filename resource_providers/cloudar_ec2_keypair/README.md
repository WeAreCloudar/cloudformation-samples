# Cloudar::EC2::KeyPair

This is a Custom Resource to import a KeyPair to EC2.

Usage:
```
MyKeyPair:
  Type: Cloudar::EC2::KeyPair
  Properties:
    KeyName: string
    PublicKey: string
```
Updating a property always requires a replacement.
