Программа предназначена для переноса значений между конфигурационными файлами оркестратора.

Ограничения текущей версии:
- Программа удаляет комментарии из конфигов;
- Не работает с connection strings MSSQL (будет исправлено в ближайшее время);
- Работает только с win версиями;

В процессе обновления версии оркестратора необходимо переименовать старые папки служб, добавив к ним окончание "-old" (например, "WebApi-old"). Ошибки в наименовании не допускаются. В той же папке развернуть новые дистрибутивы служб оркестратора без изменения названий. В корень этой папки поместить данную программу и запустить. В процессе работы программа сформирует файл "Log.txt", содержащий информацию о процессе переноса.

Принцип работы.
1. Производится проверка версий. Значение версии берется из файла Readme WebApi.
  Для каждой службы
2. Делается бэкап изначальных файлов конфигурации;
3. Файлы конфигурации очищаются от комментариев;
4. Выполняется проверка версий. Если старая версия старше или равна 23.2, а новая новее или равна 23.4, то конфигурационный файл службы RDP2 не изменяется;
5. Запускается последовательное чтение всех элементов старого конфиг-файла. Алгоритм перебирает ключи на всех уровнях вложенности. Для каждого ключа формируется адрес, по которому происходит запись значения ключа в новый файл.
