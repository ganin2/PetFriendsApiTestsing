import requests

from api import PetFriends
from settings import valid_email, valid_password, invalid_password, invalid_email
import os

pf = PetFriends()


def test_get_api_key_for_valid_user(email=valid_email, password=valid_password):
    """ Проверяем что запрос api ключа возвращает статус 200 и в  результате содержится слово key"""

    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
    status, result = pf.get_api_key(email, password)

    # Сверяем полученные данные с нашими ожиданиями
    assert status == 200
    assert 'key' in result


def test_get_all_pets_with_valid_key(filter=''):
    """ Проверяем что запрос всех питомцев возвращает не пустой список.
    Для этого сначала получаем api ключ и сохраняем в переменную auth_key. Далее используя этого ключ
    запрашиваем список всех питомцев и проверяем что список не пустой.
    Доступное значение параметра filter - 'my_pets' либо '' """

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter)

    assert status == 200
    assert len(result['pets']) > 0


def test_add_new_pet_with_valid_data(name='Барбоскин', animal_type='двортерьер',
                                     age='4', pet_photo='images/cat1.jpg'):
    """Проверяем что можно добавить питомца с корректными данными"""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == name


def test_successful_delete_self_pet():
    """Проверяем возможность удаления питомца"""

    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, "Суперкот", "кот", "3", "images/cat1.jpg")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Берём id первого питомца из списка и отправляем запрос на удаление
    pet_id = my_pets['pets'][0]['id']
    status, _ = pf.delete_pet(auth_key, pet_id)

    # Ещё раз запрашиваем список своих питомцев
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем что статус ответа равен 200 и в списке питомцев нет id удалённого питомца
    assert status == 200
    assert pet_id not in my_pets.values()


def test_successful_update_self_pet_info(name='Мурзик', animal_type='Котэ', age=5):
    """Проверяем возможность обновления информации о питомце"""

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Еслди список не пустой, то пробуем обновить его имя, тип и возраст
    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)

        # Проверяем что статус ответа = 200 и имя питомца соответствует заданному
        assert status == 200
        assert result['name'] == name
    else:
        # если спиок питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception("There is no my pets")


def test_add_new_pet_without_photo (name='Шарикs', animal_type='алабайs',
                                         age='11'):
    """Проверяем что можно добавить питомца с корректными данными без фото"""
    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    # Добавляем питомца без фото
    status, result = pf.add_new_pet_without_photo(auth_key, name, animal_type, age )
    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == name


def test_successful_update_self_new_photo_pet(pet_photo='images/cat2.jpg'):
    """Проверяем возможность обновления информации о питомце а именно фото """

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, "Суперкот", "кот", "3", "images/cat1.jpg")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    res1=my_pets['pets'][0]['pet_photo']

    # меняем фото у 0 питомца
    status, result = pf.Add_new_photo_pet(auth_key, my_pets['pets'][0]['id'], pet_photo)
    # Проверяем что статус ответа = 200 и сравниваем фото- они должны быть разные
    assert status == 200
    assert result['pet_photo'] != res1


def test_get_api_key_for_invalid_password(email=valid_email, password=invalid_password):
    """ Проверяем что при вводе неправильного пароля запрос api ключа не возвращает статус 200 и
    в  результате не содержится слово key"""

    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
    status, result = pf.get_api_key(email, password)
    # Сверяем полученные данные с нашими ожиданиями что нельзя получить ключи с неправильным паролем
    assert status != 200
    assert 'key' is not result


def test_get_api_key_for_invalid_email (email=invalid_email, password=valid_password):
    """ Проверяем что при вводе незарегистрированного email запрос api ключа не возвращает статус 200 и
    в  результате не содержится слово key"""

    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
    status, result = pf.get_api_key(email, password)
    # Сверяем полученные данные с нашими ожиданиями что нельзя получить ключи с неправильным email
    assert status != 200
    assert 'key' is not result

def test_successful_update_self_new_big_photo_pet(pet_photo='images/file_7Mb_JPG.jpg'):
    """Проверяем возможность добавления фото больше 6мБ"""

    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    # Если список не пустой, то пробуем обновить его фото
    if len(my_pets['pets']) > 0:
        status, result = pf.Add_new_photo_pet(auth_key, my_pets['pets'][0]['id'], pet_photo)
        # Проверяем что статус ответа = 200 и имя питомца соответствует заданному
        assert status == 200
    else:
        # если спиок питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception("There is no my pets")

def test_add_new_pet_big_characters_in_name (name='LRkKCt3mBg2NQoAk1RXQXXhZAqI5Hd74uvIWFvUblNP3FdbMzfhyK4OQ2wqw8B0g67zxlYD1UYv5j42RzuQROe0dzOELuPRhnN2JDzcg38KXs4AsJ95JCoRQBIqNJ8m7AcznFjpcLubkB832Y8nwBlpgm9JMNrS5Qbl5Q6rMj54QUHZjibaKbywEs6JJRDMrmn60h91pcVHtzDOlSC1MIWg0z0sA7zqZImH1SEYtZwOQ6WbIL1IcF0VUWGelDCS',
                                             animal_type='алабайs',age='5'):
    """Проверяем что можно добавить питомца с именем в 255 символов"""
    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    # Добавляем питомца
    status, result = pf.add_new_pet_without_photo(auth_key, name, animal_type, age )
    # Сверяем полученный ответ с ожидаемым результатом: ожидаем что будет ошибка
    assert status == 200
    assert result['name'] == name

def test_add_new_pet_negative_value_age (name='Тузикс', animal_type='спаниель',
                                         age='-5'):
    """Проверяем что можно добавить питомца с отрицательны возрастом"""
    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    # Добавляем питомца
    status, result = pf.add_new_pet_without_photo(auth_key, name, animal_type, age )
    # Сверяем полученный ответ с ожидаемым результатом: ожидаем ошибку. Это баг- приложение записывает питомца с отрицательным возрастом
    assert status == 200
    assert result['name'] == name


def test_add_new_pet_empty_value_name(name='', animal_type='спаниель',
                                   age='2'):
    """Проверяем что можно добавить питомца с пустым полем имя"""
    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    # Добавляем питомца
    status, result = pf.add_new_pet_without_photo(auth_key, name, animal_type, age)
    # Сверяем полученный ответ с ожидаемым результатом: ожидаем ошибку
    assert status == 200
    assert result['name'] == name

def test_add_new_pet_empty_value_name_and_animal_type (name='', animal_type='',
                                   age='2'):
    """Проверяем что можно добавить питомца с пустыми полями имя и вид животного"""
    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    # Добавляем питомца
    status, result = pf.add_new_pet_without_photo(auth_key, name, animal_type, age)
    # Сверяем полученный ответ с ожидаемым результатом: ожидаем ошибку. Это баг
    assert status == 200
    assert result['name'] == name


def test_impossible_delete_any_pet():
    """Проверяем возможность удаления чужого питомца берем номер 8 """
    # Получаем ключ auth_key и запрашиваем список всех питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter='')
    # сохраняем в переменные id и имя восьмого питомца из списка
    res1 = result['pets'][8]['id']
    res2 = result['pets'][8]['name']
    # выводим на печать их значения
    print(result['pets'][8]['id'])
    print(result['pets'][8]['name'])
    # Берём id восьмого питомца из списка и отправляем запрос на удаление
    pet_id = result['pets'][8]['id']
    status, _ = pf.delete_pet(auth_key, pet_id)

    # Ещё раз запрашиваем список всех питомцев
    status, result = pf.get_list_of_pets(auth_key, filter='')
    # Проверяем что статус ответа равен 200 и под номером 8 другой питомец: другое имя и id. Это баг
    assert status == 200
    assert result['pets'][8]['id'] != res1
    assert result['pets'][8]['name'] != res2
    # выводим на печать новые имя и id восьмого питомца
    print(result['pets'][8]['id'])
    print(result['pets'][8]['name'])

def test_successful_update_self_new_photo_pet_PNG (pet_photo='images/tiger_001_PNG.png'):
    """Проверяем возможность добавления фото питомца в формате PNG"""

    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    # Если список не пустой, то пробуем обновить его фото
    if len(my_pets['pets']) > 0:
        status, result = pf.Add_new_photo_pet_PNG(auth_key, my_pets['pets'][0]['id'], pet_photo)
        # Проверяем что статус ответа не равен 200. Это баг т.к. в документации написано что этот формат использовать можно
        assert status != 200
    else:
        raise Exception("There is no my pets")


def test_successful_update_self_new_photo_pet_JPEG(pet_photo='images/dogBIG_JPEG.jpeg'):
        """Проверяем возможность добавления фото  в формате JPEG """

        pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
        # Получаем ключ auth_key и список своих питомцев
        _, auth_key = pf.get_api_key(valid_email, valid_password)
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
        # Если список не пустой, то пробуем обновить его фото
        if len(my_pets['pets']) > 0:
            status, result = pf.Add_new_photo_pet_JPEG(auth_key, my_pets['pets'][0]['id'], pet_photo)
            # Проверяем что статус ответа = 200
            assert status == 200
        else:
            # если спиок питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
            raise Exception("There is no my pets")


def test_successful_update_self_new_photo_pet_GIF(pet_photo='images/dogGIF.gif'):
    """Проверяем возможность добавления фото  в формате GIF """

    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    # Если список не пустой, то пробуем обновить его фото
    if len(my_pets['pets']) > 0:
        status, result = pf.Add_new_photo_pet_GIF(auth_key, my_pets['pets'][0]['id'], pet_photo)
        # Проверяем что статус ответа не равен 200 и имя питомца соответствует заданному
        assert status != 200
    else:
        # если спиок питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception("There is no my pets")






