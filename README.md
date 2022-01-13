# Mares

It is needed to edit the `pendulum.ini` file and make sure that the DEV_PORT (/dev/ttyAMA0 or /dev/ttyS0) is corect for your pendulum, and after that you can test the script with the comand:

```
sh start.sh
```

after that you will need to configur the crontab using the comand:

```
crontab -e
```

and going to the last line, and  past the following code on it:

```
 */23 * * * * cd $path to the file$; sh start.sh
```