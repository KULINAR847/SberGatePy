# SberGatePy
Оболочка для работы с библиотекой gate.dll от сбербанка

* Для автоматического поиска терминала необходим модуль для работы с COM:
pip install pyserial

### Создаём инстанс для работы с терминалом сбера
sber = SberGate()
* Уже можем оплатить что-то
#print(sber.Pay(7000))
* Но вначале надо проверить готовность пинпада
#print(sber.PinPadReady())
* Сделаем возврат
#print(sber.Ret(1000))
* Возникли проблемы смотрим описание ошибки
#print(sber.getErrorDesc(4113))
* Если нужно выяснить, что-то по карте
#error, card_number, card_hash = sber.GetCardHash()
* Или узнать информацию по терминалу
#error, TermNum, MerchNum = sber.GetTerminalNumber()
* Сверим итоги
#sber.ZReport()
* Если всё хорошо то вот он чек
#cheque = sber.cheque_text
