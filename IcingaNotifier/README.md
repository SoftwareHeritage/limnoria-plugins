Pipe Icinga notifications to your channel

Icinga service notification script:

    #!/bin/sh
    template=`cat <<TEMPLATE
    {
        "notification_type": "$NOTIFICATIONTYPE",
        "host": "$HOSTALIAS",
        "service": "$SERVICEDESC",
        "hostdisplay": "$HOSTDISPLAYNAME",
        "servicedisplay": "$SERVICEDISPLAYNAME",
        "address": "$HOSTADDRESS",
        "state": "$SERVICESTATE",
        "datetime": "$LONGDATETIME",
        "message": "$SERVICEOUTPUT",
        "author": "$NOTIFICATIONAUTHORNAME",
        "comment": "$NOTIFICATIONCOMMENT"
    }
    `
    
    /usr/bin/printf "%b" "$template" | curl -d@- -H 'Content-Type: application/json' http://<limnoria http server>/icinga/<network>.<percent-encoded channel name>

Icinga host notification script:

    #!/bin/sh
    template=`cat <<TEMPLATE
    {
        "notification_type": "$NOTIFICATIONTYPE",
        "host": "$HOSTALIAS",
        "hostdisplay": "$HOSTDISPLAYNAME",
        "address": "$HOSTADDRESS",
        "state": "$HOSTSTATE",
        "datetime": "$LONGDATETIME",
        "message": "$HOSTOUTPUT",
        "author": "$NOTIFICATIONAUTHORNAME",
        "comment": "$NOTIFICATIONCOMMENT"
    }
    `
    
    /usr/bin/printf "%b" "$template" | curl -d@- -H 'Content-Type: application/json' http://<limnoria http server>/icinga/<network>.<percent-encoded channel name>
    
