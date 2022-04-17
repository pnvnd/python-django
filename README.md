# Instructions
Check out the deployed app at https://datacrunch-python-django.herokuapp.com/

1. `python -m venv venv`
2. `.\venv\Scripts\Activate.ps1`
3. `pip install -r requirements.txt`
4. `python -m pip install --upgrade pip`
5. `python manage.py migrate` (optional)
6. `python manage.py runserver`
7. Go to http://127.0.0.1:8000

# OpenTelemetry
1. Check out the OTEL settings in `learning_logs/view.py`
2. Set the following environment variables:
    ```PowerShell
    $env:DJANGO_SETTINGS_MODULE="learning_log.setting"
    $env:OTEL_EXPORTER_OTLP_ENDPOINT="https://otlp.nr-data.net:4317"
    $env:OTEL_EXPORTER_OTLP_HEADERS="api-key=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXNRAL"
    $env:OTEL_LOGS_EXPORTER="otlp"
    $env:OTEL_METRICS_EXPORTER="otlp"
    $env:OTEL_METRIC_EXPORT_INTERVAL="1000"
    $env:OTEL_RESOURCE_ATTRIBUTES="service.name=python-django.local,service.instance.id=localhost"
    ```

3. `python manage.py runserver --noreload`
