# Makefile for the GitHub Universe knowledge base. See README.md.

.DEFAULT_GOAL := default

# Use only the checked-in project configuration. Otherwise uv merges user- and
# system-level settings into uv.lock, which can make it fail on another machine.
UV_CONFIG_FILE := $(CURDIR)/uv.toml
export UV_CONFIG_FILE

# Safe default for every dependency resolution invoked through this Makefile.
UV_EXCLUDE_NEWER ?= 14 days
export UV_EXCLUDE_NEWER

.PHONY: default install lint test build validate

default: install lint test

install:
	uv sync --all-groups

lint:
	uv run ruff check
	uv run basedpyright

test:
	uv run pytest

build:
	uv run universe-kb build

validate:
	uv run universe-kb validate
