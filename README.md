# SanctaMaria

An API for Sancta Maria school, nz

## Initialise
```python
from smc import SanctaMaria

school = SanctaMaria()
```

## Get News
```python
page_num = school.getNews() #Get Number Of Pages
school.getNews(1) #Get First Page
school.getNews(page_num) #Get Last Page
```

## Login
```python
school.portal.login(ID, PASSWORD)
school.schoology.login(ID, PASSWORD)
```
