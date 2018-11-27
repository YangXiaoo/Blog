#!/bin/bash
# myweb 
# chkconfig: - 85 12
# description: startup script for myweb
# 2018-11-25

myweb_dir=
base_dir=$(dirname $0)
myweb_dir=${myweb_dir:-$base_dir}
export PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
if [ -f ${sshserver_dir}/install/functions ];then
    . ${sshserver_dir}/install/functions
elif [ -f /etc/init.d/functions ];then
    . /etc/init.d/functions
else
    echo "No functions script found in [./functions, ./install/functions, /etc/init.d/functions]"
    exit 1
fi
PROC_NAME="myweb"
lockfile=/var/lock/subsys/${PROC_NAME}

start() {
    if [ $(whoami) != 'root' ];then
        echo "Sorry, myweb must be run as root."
        exit 1
    fi

    myweb_start=$"Starting ${PROC_NAME} server:"
    if [ -f $lockfile ];then
        echo -n "myweb is running..."
        success "$myweb_start"
    else
        # daemon python $myweb_dir/manage.py crontab add &>> /var/log/ssh.log 2>&1 #add crontab
        nginx -s stop &> /dev/null 2>&1 &
        service httpd stop &> /dev/null 2>&1 &
        pkill php-fpm &> /dev/null 2>&1 &
        daemon python $myweb_dir/run_server.py &> /dev/null 2>&1 &
        sleep 1
        echo -n "$myweb_start"
        ps axu | grep 'run_server' | grep -v 'grep' &> /dev/null  # &> equal 2>&1
        if [ $? == '0' ];then
            success "$myweb_start" 
            if [ ! -e $lockfile ]; then # if file is not exist
                lockfile_dir=`dirname $lockfile` # return /var/lock/subsys
                # -v, --verbose    print a message for each created directory
                mkdir -pv $lockfile_dir 
            fi
            touch "$lockfile"
            echo
        else
            failure "$myweb_start"
            echo
        fi
    fi

}

stop() {
    echo -n $"Stopping ${PROC_NAME} service:"
    # daemon python $sshserver_dir/manage.py crontab remove &>> /var/log/ssh.log 2>&1
    ps aux | grep -E 'run_server.py' | grep -v grep | awk '{print $2}' | xargs kill -9 &> /dev/null
    ret=$?
    if [ $ret -eq 0 ]; then
        echo_success
        echo
        rm -f "$lockfile"
    else
        echo_failure
        echo
        rm -f "$lockfile"
    fi

}

status(){
    ps axu | grep 'run_server' | grep -v 'grep' &> /dev/null  # successful 0, fail 1
    if [ $? == '0' ];then
        echo -n "myweb is running..."
        success
        touch "$lockfile"
        echo
    else
        echo -n "myweb is not running."
        failure
        echo
    fi
}


restart(){
    stop
    start
}

case "$1" in 
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    status)
        status
        ;;
    *)
        echo $"Usage: $0 {start|stop|restart|status}"
        exit 2
esac
