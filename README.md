# Shakespearch

This is the first assignment of COMP0054 (Principle of Information Retrieval System), which taught by Dr. [Yanlong Wen](http://cc.nankai.edu.cn/Teachers/Introduce.aspx?TID=wenyl) in Nankai University.

## Introduction

The name of this project, "Shakespearch", stands for "Shakespeare" and "search". I developed a website to simplify the querying procedure.

## Dependency

*It is my own environment. To reproduce, plz follow it.*

1. Ubuntu 16.04.3 LTS
2. python 3.5.2 64-bit
3. nltk 3.2.5 (Note: plz download all dependent modules using command `python3 -m nltk.downloader all`)
4. pandas 0.20.3
5. dill 0.2.7.1
6. Flask 0.12.2

## How to Reproduce

### Install Necessary Linux Modules

```bash
$ sudo apt-get update
$ sudo apt-get install python3-dev python3-pip
$ sudo apt-get install git build-essential libssl-dev libevent-dev libjpeg-dev libxml2-dev libxslt-dev
$ sudo apt-get upgrade
```

### Install Python Modules

```bash
$ sudo pip3 install nltk pandas dill flask
```

### Download `nltk` Data

```bash
$ python3 -m nltk.downloader all
```

### Clone the Project

*Note: it is not necessary if you have already got the source code.*

```bash
$ git clone https://github.com/Pika7ma/Shakespearch.git
```

### Load Articles

*Note: it is not necessary if there is already `articles.pkl` in the root folder.*

```bash
$ cd Shakespearch
$ python3 articles
```

### Run the Server

```bash
$ python3 web.py
```

Then the console should tell you:

```bash


In order to complete this project, I downloaded "The Complete Works of William Shakespeare" from [Folger Shakespeare Digital Library](http://www.folgerdigitaltexts.org/download/)
