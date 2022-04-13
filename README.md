# Project Title

Project 1 for Headstarter Accelerate

## Description

This project is a script that runs over a directory of files scanning for sensitive data. If any sensitive data is found, it will send an email to the configured user alerting them which type of data was found.

## Getting Started

### Executing program

There are 2 ways to use this script. 

## Option 1. Use the Leak_Searcher Class
This method allows you to use Python code to create a leak_searcher object and pass it information such as the relative directory you want to search, sender & receiver emails, and more. <br/>
Next, you can call `scan_dir_files('foo/')` on the object to scan all files in the passed directory for sensitive info. See **sandbox.py** for example code.

## Option 2. Call the script from the terminal.
1. Add the "**Project**" directory to your PATH environment variables.

You can run the script without arguments. This runs it on the current working directory. The following command runs the script in **C:\Users\Foo\Documents\\**.
```
C:\Users\Foo\Documents> generate_email.py
```

<br/>

Or you can pass a relative path to a directory as an argument, and the script will run on the passed directory. The following command runs the script in **C:\Users\Foo\Documents\foo\bar\\**.
```
C:\Users\Foo\Documents> generate_email.py foo/bar/
```

## Improvements That Could Be Made
* Time complexity of the regex replacement. Currently, the entire file is scanned for every regex operation. This could be improved by reading the file line by line.
* **Leak_Searcher.py** and **generate_email.py** have duplicated code. Improving the code in one file means it also has to be copied to the other.