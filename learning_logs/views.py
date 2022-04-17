from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import Http404

from .models import Topic, Entry
from .forms import TopicForm, EntryForm

# OpenTelemetry Settings Imports
from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.instrumentation.sqlite3 import SQLite3Instrumentor
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.urllib3 import URLLib3Instrumentor
from opentelemetry.instrumentation.urllib import URLLibInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor

from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

import logging
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.sdk._logs import LogEmitterProvider
from opentelemetry.sdk._logs import set_log_emitter_provider
from opentelemetry.sdk._logs import OTLPHandler
from opentelemetry.sdk._logs.export import BatchLogProcessor

from opentelemetry.sdk.resources import Resource

# OpenTelemetry Settings
import uuid
serviceId = str(uuid.uuid1())

trace.set_tracer_provider(TracerProvider(resource=Resource.create({"service.name": "python-django.heroku", "service.instance.id": serviceId, "environment": "production"})))
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))

log_emitter_provider = LogEmitterProvider(resource=Resource.create({"service.name": "python-django.heroku", "service.instance.id": serviceId, "environment": "production"}))
set_log_emitter_provider(log_emitter_provider)

exporter = OTLPLogExporter(insecure=True)
log_emitter_provider.add_log_processor(BatchLogProcessor(exporter))
log_emitter = log_emitter_provider.get_log_emitter(__name__, "0.1")
handler = OTLPHandler(level=logging.DEBUG, log_emitter=log_emitter)

# Attach OTLP handler to root logger
logging.getLogger().addHandler(handler)

DjangoInstrumentor().instrument()
SQLite3Instrumentor().instrument()
Psycopg2Instrumentor().instrument()
RequestsInstrumentor().instrument()
URLLib3Instrumentor().instrument()
URLLibInstrumentor().instrument()
LoggingInstrumentor().instrument(log_level=logging.DEBUG)

# Create your views here.

def check_topic_owner(owner, request):
    # Make sure the topic belongs to the current user.
    if owner != request.user:
        raise Http404

def index(request):
    """The home page for Learning Log."""
    return render(request, 'learning_logs/index.html')

@login_required
def topics(request):
    """Show all topics."""
    topics = Topic.objects.order_by('date_added') # filter(owner=request.user).
    context = {'topics': topics}
    return render(request, 'learning_logs/topics.html', context)

@login_required
def topic(request, topic_id):
    """Show a single topic and all of its entrees."""
    topic = get_object_or_404(Topic, id=topic_id)
    # check_topic_owner(topic.owner, request)
    entries = topic.entry_set.order_by('-date_added')
    context = {'topic': topic, 'entries': entries}
    return render(request, 'learning_logs/topic.html', context)

@login_required
def new_topic(request):
    """Add a new topic."""
    if request.method != 'POST':
        # No data submitted; create a blank form.
        form = TopicForm()
    else:
        # POST data submitted; process data.
        form = TopicForm(data=request.POST)
        if form.is_valid():
            new_topic = form.save(commit=False)
            new_topic.owner = request.user
            new_topic.save()
            return redirect('learning_logs:topics')

    # Display a blank or invalid form.
    context = {'form': form}
    return render(request, 'learning_logs/new_topic.html', context)

@login_required
def new_entry(request, topic_id):
    """Add a new entry for a particular topic."""
    topic = Topic.objects.get(id=topic_id)
    # check_topic_owner(topic.owner, request)

    if request.method != 'POST':
        # No data submitted; create a blank form.
        form = EntryForm()
    else:
        # POST data submitted; process data.
        form = EntryForm(data=request.POST)
        if form.is_valid():
            new_entry = form.save(commit=False)
            new_entry.topic = topic
            new_entry.save()
            return redirect('learning_logs:topic', topic_id=topic_id)

    # Display a blank or invalid form.
    context = {'topic': topic, 'form': form}
    return render(request, 'learning_logs/new_entry.html', context)

@login_required
def edit_entry(request, entry_id):
    """Edit an existing entry."""
    entry = Entry.objects.get(id=entry_id)
    topic = entry.topic
    check_topic_owner(topic.owner, request)

    if request.method != 'POST':
        # Initial request; pre-fill form with current entry.
        form = EntryForm(instance=entry)
    else:
        # POST data submitted; process data.
        form = EntryForm(instance=entry, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('learning_logs:topic', topic_id=topic.id)

    context = {'entry': entry, 'topic': topic, 'form': form}
    return render(request, 'learning_logs/edit_entry.html', context)
