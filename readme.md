telegram-mailgate
=================

telegram-mailgate очень похож на [gpg-mailgate](https://github.com/uakfdotb/gpg-mailgate).
Этот скрипт является контент-фильтром для Postfix для отправки почты через telegram.
Он очень минималистичен, но может быть полезен для получения выходных данных say от CRON непосредственно на ваш мобильный телефон.

    usage: telegram-mailgate.py [-h] [--config CONFIG] [--from FROM]
                                [--queue-id QUEUE_ID] 
                                to [to ...]
    
    positional arguments:
      to                   the recipients
    
    optional arguments:
      -h, --help           показать это справочное сообщение и выйти
      --config CONFIG      использовать пользовательский конфигурационный файл
      --from FROM          перезаписать поле "From" из заголовка
      --queue-id QUEUE_ID  идентификатор очереди сообщений для отладки

Установка (Centos 8)
------------

    sudo dnf update 
    sudo dnf install python3 python3-pip
    sudo adduser --system telegram-mailer  # создайте отдельного пользователя для запуска telegram-mailgate
    sudo -u telegram-mailer pip3 install --user pyTelegramBotAPI
    git clone https://github.com/EvgeniyAlf/telegram-mailgate.git
    sudo cp telegram-mailgate/telegram-mailgate.py /usr/local/bin/
    sudo chown telegram-mailer /usr/local/bin/telegram-mailgate.py
    sudo chmod 700 /usr/local/bin/telegram-mailgate.py
    sudo mkdir /etc/telegram-mailgate
    sudo cp telegram-mailgate/{main.cf,logging.cf,aliases} /etc/telegram-mailgate/    

Редактирование `/etc/telegram-mailgate/main.cf` для конфигурирования вашего telegram API key.
Редактирование `/etc/telegram-mailgate/aliases` чтобы настроить сопоставление адресов получателей и соответствующего идентификатора чата.

Формат:
    EvgeniyAlf 00000000
    Bob 00000001
    Charlie 00000002

Формат не поддерживает комментарии и пустые строки.

Вы можете дополнительно отредактировать файл `/etc/telegram-mailgate/logging.cf` для настройки ведения журнала. Журналы по умолчанию записываются в системный журнал.

Конфигурация postfix
---------------------

В файл `/etc/postfix/master.cf`, добавьте следующий процесс:

    # =======================================================================
    # telegram-mailgate
    telegram-mailgate unix -     n       n       -        -      pipe
      flags= user=telegram-mailer argv=/usr/local/bin/telegram-mailgate.py --queue-id $queue_id $recipient

Убедитесь, что любой пользователь, указанный выше, имеет разрешения на выполнение установленных зависимостей telegram-mailgate и python. Конечно, вы можете задать любые аргументы для скрипта.
    
В файл `/etc/postfix/main.cf` добавьте telegram-mailgate в качестве фильтра контента:

    content_filter = telegram-mailgate
    
Restart postfix

    # postfix reload

Тестирование
-------

    echo "This is the body of the email" | mail -s "This is the subject line" <my_recipent>

замените <my_recipient> тем, кто когда-либо был указан в файле псевдонима. Если вы локальный пользователь, вам может потребоваться добавить @<hostname> в конце.
Вы можете видеть журналы с помощью `sudo tail-f /var/log/mail.log`.
