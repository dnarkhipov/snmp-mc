Прототипирование элементов системы управления Менеджер/Агент (SNMPv3)
-----------------------------------------

Прототипирование элементов системы управления специальным оборудованием.
Отрабатывается схема взаимодействия элементов Менеджер-Агент по протоколу SNMPv3.

Агент
------
- Принимает управляющие команды по протоколу SNMPv3
- При наступлении определенных событий генерирует SNMP-Inform сообщения для Менеджера
- По поступающим командам формирует команды управления удаленной системой по специальному протоколу
- Принимает от удаленной системы по специальному протоколу телеметрию

Менеджер
--------
- Реализует HTTP-RESTFull API для систем верхнего уровня
- Взаимодействует с Агентом по протоколу SNMPv3
