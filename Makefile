.PHONY: help doctor check validate validate-changed validate-all \
	firmware-host firmware app server remote openspec

help:
	@./scripts/repo-harness help

doctor:
	@./scripts/repo-harness doctor

check:
	@./scripts/repo-harness check

validate:
	@./scripts/repo-harness validate quick

validate-changed:
	@./scripts/repo-harness validate changed

validate-all:
	@./scripts/repo-harness validate all

firmware-host:
	@./scripts/repo-harness validate firmware-host

firmware:
	@./scripts/repo-harness validate firmware

app:
	@./scripts/repo-harness validate app

server:
	@./scripts/repo-harness validate server

remote:
	@./scripts/repo-harness validate remote

openspec:
	@./scripts/repo-harness validate openspec
