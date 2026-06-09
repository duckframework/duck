# {py:mod}`duck.utils.dateutils`

```{py:module} duck.utils.dateutils
```

```{autodocx-docstring} duck.utils.dateutils
:allowtitles:
```

## Module Contents

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`build_readable_date <duck.utils.dateutils.build_readable_date>`
  - ```{autodocx-docstring} duck.utils.dateutils.build_readable_date
    :summary:
    ```
* - {py:obj}`calculate_date_diff <duck.utils.dateutils.calculate_date_diff>`
  - ```{autodocx-docstring} duck.utils.dateutils.calculate_date_diff
    :summary:
    ```
* - {py:obj}`convert_timezone <duck.utils.dateutils.convert_timezone>`
  - ```{autodocx-docstring} duck.utils.dateutils.convert_timezone
    :summary:
    ```
* - {py:obj}`datetime_difference <duck.utils.dateutils.datetime_difference>`
  - ```{autodocx-docstring} duck.utils.dateutils.datetime_difference
    :summary:
    ```
* - {py:obj}`datetime_difference_from_now <duck.utils.dateutils.datetime_difference_from_now>`
  - ```{autodocx-docstring} duck.utils.dateutils.datetime_difference_from_now
    :summary:
    ```
* - {py:obj}`datetime_difference_upto_now <duck.utils.dateutils.datetime_difference_upto_now>`
  - ```{autodocx-docstring} duck.utils.dateutils.datetime_difference_upto_now
    :summary:
    ```
* - {py:obj}`days_to_seconds <duck.utils.dateutils.days_to_seconds>`
  - ```{autodocx-docstring} duck.utils.dateutils.days_to_seconds
    :summary:
    ```
* - {py:obj}`django_short_local_date <duck.utils.dateutils.django_short_local_date>`
  - ```{autodocx-docstring} duck.utils.dateutils.django_short_local_date
    :summary:
    ```
* - {py:obj}`format_date <duck.utils.dateutils.format_date>`
  - ```{autodocx-docstring} duck.utils.dateutils.format_date
    :summary:
    ```
* - {py:obj}`gmt_date <duck.utils.dateutils.gmt_date>`
  - ```{autodocx-docstring} duck.utils.dateutils.gmt_date
    :summary:
    ```
* - {py:obj}`hours_to_seconds <duck.utils.dateutils.hours_to_seconds>`
  - ```{autodocx-docstring} duck.utils.dateutils.hours_to_seconds
    :summary:
    ```
* - {py:obj}`local_date <duck.utils.dateutils.local_date>`
  - ```{autodocx-docstring} duck.utils.dateutils.local_date
    :summary:
    ```
* - {py:obj}`minutes_to_seconds <duck.utils.dateutils.minutes_to_seconds>`
  - ```{autodocx-docstring} duck.utils.dateutils.minutes_to_seconds
    :summary:
    ```
* - {py:obj}`months_to_seconds <duck.utils.dateutils.months_to_seconds>`
  - ```{autodocx-docstring} duck.utils.dateutils.months_to_seconds
    :summary:
    ```
* - {py:obj}`parse_date <duck.utils.dateutils.parse_date>`
  - ```{autodocx-docstring} duck.utils.dateutils.parse_date
    :summary:
    ```
* - {py:obj}`parse_datetime <duck.utils.dateutils.parse_datetime>`
  - ```{autodocx-docstring} duck.utils.dateutils.parse_datetime
    :summary:
    ```
* - {py:obj}`parse_time <duck.utils.dateutils.parse_time>`
  - ```{autodocx-docstring} duck.utils.dateutils.parse_time
    :summary:
    ```
* - {py:obj}`seconds_to_days <duck.utils.dateutils.seconds_to_days>`
  - ```{autodocx-docstring} duck.utils.dateutils.seconds_to_days
    :summary:
    ```
* - {py:obj}`seconds_to_hours <duck.utils.dateutils.seconds_to_hours>`
  - ```{autodocx-docstring} duck.utils.dateutils.seconds_to_hours
    :summary:
    ```
* - {py:obj}`seconds_to_minutes <duck.utils.dateutils.seconds_to_minutes>`
  - ```{autodocx-docstring} duck.utils.dateutils.seconds_to_minutes
    :summary:
    ```
* - {py:obj}`seconds_to_months <duck.utils.dateutils.seconds_to_months>`
  - ```{autodocx-docstring} duck.utils.dateutils.seconds_to_months
    :summary:
    ```
* - {py:obj}`seconds_to_weeks <duck.utils.dateutils.seconds_to_weeks>`
  - ```{autodocx-docstring} duck.utils.dateutils.seconds_to_weeks
    :summary:
    ```
* - {py:obj}`seconds_to_years <duck.utils.dateutils.seconds_to_years>`
  - ```{autodocx-docstring} duck.utils.dateutils.seconds_to_years
    :summary:
    ```
* - {py:obj}`short_local_date <duck.utils.dateutils.short_local_date>`
  - ```{autodocx-docstring} duck.utils.dateutils.short_local_date
    :summary:
    ```
* - {py:obj}`weeks_to_seconds <duck.utils.dateutils.weeks_to_seconds>`
  - ```{autodocx-docstring} duck.utils.dateutils.weeks_to_seconds
    :summary:
    ```
* - {py:obj}`years_to_seconds <duck.utils.dateutils.years_to_seconds>`
  - ```{autodocx-docstring} duck.utils.dateutils.years_to_seconds
    :summary:
    ```
````

### API

````{py:function} build_readable_date(date_: dict, one_date=False) -> str
:canonical: duck.utils.dateutils.build_readable_date

```{autodocx-docstring} duck.utils.dateutils.build_readable_date
```
````

````{py:function} calculate_date_diff(start_date: datetime, end_date: datetime) -> datetime.timedelta
:canonical: duck.utils.dateutils.calculate_date_diff

```{autodocx-docstring} duck.utils.dateutils.calculate_date_diff
```
````

````{py:function} convert_timezone(date: datetime, from_timezone: str, to_timezone: str) -> datetime.datetime
:canonical: duck.utils.dateutils.convert_timezone

```{autodocx-docstring} duck.utils.dateutils.convert_timezone
```
````

````{py:function} datetime_difference(date_x: datetime.datetime, date_y: datetime.datetime) -> dict
:canonical: duck.utils.dateutils.datetime_difference

```{autodocx-docstring} duck.utils.dateutils.datetime_difference
```
````

````{py:function} datetime_difference_from_now(future_datetime: datetime.datetime) -> dict
:canonical: duck.utils.dateutils.datetime_difference_from_now

```{autodocx-docstring} duck.utils.dateutils.datetime_difference_from_now
```
````

````{py:function} datetime_difference_upto_now(previous_datetime: datetime.datetime) -> dict
:canonical: duck.utils.dateutils.datetime_difference_upto_now

```{autodocx-docstring} duck.utils.dateutils.datetime_difference_upto_now
```
````

````{py:function} days_to_seconds(days)
:canonical: duck.utils.dateutils.days_to_seconds

```{autodocx-docstring} duck.utils.dateutils.days_to_seconds
```
````

````{py:function} django_short_local_date() -> str
:canonical: duck.utils.dateutils.django_short_local_date

```{autodocx-docstring} duck.utils.dateutils.django_short_local_date
```
````

````{py:function} format_date(date: datetime, format_str: str = '%Y-%m-%d %H:%M:%S') -> str
:canonical: duck.utils.dateutils.format_date

```{autodocx-docstring} duck.utils.dateutils.format_date
```
````

````{py:function} gmt_date() -> str
:canonical: duck.utils.dateutils.gmt_date

```{autodocx-docstring} duck.utils.dateutils.gmt_date
```
````

````{py:function} hours_to_seconds(hrs)
:canonical: duck.utils.dateutils.hours_to_seconds

```{autodocx-docstring} duck.utils.dateutils.hours_to_seconds
```
````

````{py:function} local_date() -> str
:canonical: duck.utils.dateutils.local_date

```{autodocx-docstring} duck.utils.dateutils.local_date
```
````

````{py:function} minutes_to_seconds(mins)
:canonical: duck.utils.dateutils.minutes_to_seconds

```{autodocx-docstring} duck.utils.dateutils.minutes_to_seconds
```
````

````{py:function} months_to_seconds(months)
:canonical: duck.utils.dateutils.months_to_seconds

```{autodocx-docstring} duck.utils.dateutils.months_to_seconds
```
````

````{py:function} parse_date(date_str: str, format_str: str = '%d-%m-%Y') -> datetime.datetime
:canonical: duck.utils.dateutils.parse_date

```{autodocx-docstring} duck.utils.dateutils.parse_date
```
````

````{py:function} parse_datetime(datetime_str: str, format_str: str = '%d-%m-%Y %H:%M:%S') -> datetime.datetime
:canonical: duck.utils.dateutils.parse_datetime

```{autodocx-docstring} duck.utils.dateutils.parse_datetime
```
````

````{py:function} parse_time(time_str: str, format_str: str = '%H:%M:%S') -> datetime.datetime
:canonical: duck.utils.dateutils.parse_time

```{autodocx-docstring} duck.utils.dateutils.parse_time
```
````

````{py:function} seconds_to_days(secs)
:canonical: duck.utils.dateutils.seconds_to_days

```{autodocx-docstring} duck.utils.dateutils.seconds_to_days
```
````

````{py:function} seconds_to_hours(secs)
:canonical: duck.utils.dateutils.seconds_to_hours

```{autodocx-docstring} duck.utils.dateutils.seconds_to_hours
```
````

````{py:function} seconds_to_minutes(secs)
:canonical: duck.utils.dateutils.seconds_to_minutes

```{autodocx-docstring} duck.utils.dateutils.seconds_to_minutes
```
````

````{py:function} seconds_to_months(secs)
:canonical: duck.utils.dateutils.seconds_to_months

```{autodocx-docstring} duck.utils.dateutils.seconds_to_months
```
````

````{py:function} seconds_to_weeks(secs)
:canonical: duck.utils.dateutils.seconds_to_weeks

```{autodocx-docstring} duck.utils.dateutils.seconds_to_weeks
```
````

````{py:function} seconds_to_years(secs)
:canonical: duck.utils.dateutils.seconds_to_years

```{autodocx-docstring} duck.utils.dateutils.seconds_to_years
```
````

````{py:function} short_local_date() -> str
:canonical: duck.utils.dateutils.short_local_date

```{autodocx-docstring} duck.utils.dateutils.short_local_date
```
````

````{py:function} weeks_to_seconds(weeks)
:canonical: duck.utils.dateutils.weeks_to_seconds

```{autodocx-docstring} duck.utils.dateutils.weeks_to_seconds
```
````

````{py:function} years_to_seconds(yrs)
:canonical: duck.utils.dateutils.years_to_seconds

```{autodocx-docstring} duck.utils.dateutils.years_to_seconds
```
````
