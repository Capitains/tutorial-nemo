Preparing your environment
===

**Important:** For convenience, the following command will assume we are working in a folder named `nemo-app` at the root of your home folder (so that `cd ~/nemo-app` would work and leads you at the root of your application)

# Setting up python

## Ubuntu and derivatives such as Linux Mint

You'll need to do the following commands. You need to have sudo rights.

### Install python 3

Make sure to type this command on a terminal. 

```shell
sudo apt-get install python3 libfreetype6-dev python3-pip python3-virtualenv libxml2 libxml2-dev python3-dev libxslt1-dev
```

Once it has been done, in the directory where you will develop your application, you'll set up a [virtual environment](http://docs.python-guide.org/en/latest/dev/virtualenvs/#lower-level-virtualenv). A virtual environment is - to make it simple - a closed, independent version of python that will only be used in the context of your project.

```shell
virtualenv env -p python3
```

Now you can simply source your virtual environment.

```shell
source env/bin/activate
```

If you type `which python` it should now show `/home/USERNAME/nemo-app/env/bin/python` where USERNAME is your username. Also, your shell might probably move from `USERNAME@COMPUTERNAME $:` to `(env) USERNAME@COMPUTERNAME $:`. You will need to type this command everytime you want to work with your Nemo-App

# Setting Up the Dependencies

This tutorial has been developed with Nemo (Version: 1.0.1) and Nautilus (Version: 1.0.1). To install them, while in your virtual environment, type

```sh
pip install flask-nemo==1.0.1 capitains_nautilus==1.0.1
```

# Setting up your data

In the context of this tutorial, we are gonna use the data from the Lasciva Roma Project which contains a small set
of Latin texts with some translations. We are use both [Additional Texts](https://github.com/lascivaroma/additional-texts)
and [Priapeia corpora](https://github.com/lascivaroma/priapeia).

You'll need to unzip or download the data. We will unzip them in `corpora` so that the hierarchies of folders are :

- /corpora
	- /priapeia
		- README.md
		- /data
			- ...
	- /additional-texts
		- README.md
		- /data
			- ...

You can do that manually via your OS graphical interface or this can be executed from command line doing :

```sh
# Creating the directory
mkdir corpora
# Downloading Priapeia corpora
wget https://github.com/lascivaroma/priapeia/archive/master.zip
# Unzipping the zip : results in corpora/priapeia-master instead of corpora/priapeia
unzip master.zip -d corpora/
# Moving corpora/priapeia-master to corpora/priapeia
mv corpora/priapeia-master corpora/priapeia
# Removing the zip
rm master.zip

# Same commands for Additional-Texts

wget https://github.com/lascivaroma/additional-texts/archive/master.zip
unzip master.zip -d corpora/
mv corpora/additional-texts-master corpora/additional-texts
rm master.zip
```

# Next

Go to [1) Setting up the bases of your app](1-setting-up-the-app.md)