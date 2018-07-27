from distutils.core import setup

setup(
    #Application name
    name="TelegramChatManager",

    #Version Number
    version="0.1.0",

    #Application Author details
    author="Frank Fichtenmueller",
    author_email="frank.fichtenmueller@outlook.com",

    #Packages
    packages=["app"],

    #Include additional files into the package
    include_package_data=True,

    #Details
    url="",

    long_description=open("README.txt").read(),

    #Dependent packages (distributions)
    install_requires=[
        "telethon",
        "pandas"
    ],


)