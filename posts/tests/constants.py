from django.urls import reverse


NEW_URL = reverse('new_post')
INDEX_URL = reverse('index')
SLUG = 'test'
GROUP_URL = reverse('group', args=[SLUG])
AUTHOR_URL = reverse('about:author')
TECH_URL = reverse('about:tech')
NOT_FOUND_URL = reverse('404')
SERVER_ERROR_URL = reverse('500')
SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x01\x00'
    b'\x01\x00\x00\x00\x00\x21\xf9\x04'
    b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
    b'\x00\x00\x01\x00\x01\x00\x00\x02'
    b'\x02\x4c\x01\x00\x3b'
)
TITLE = 'Тестовый заголовок'
DESCRIPTION = 'Описание тестовой группы'
TEXT = 'Тестовый тест'
PUB_DATE = '06.01.2021'
TITLE_2 = 'Тестовый заголовок второй'
SLUG_2 = 'second-slug'
DESCRIPTION_2 = 'Описание второй тестовой группы'
