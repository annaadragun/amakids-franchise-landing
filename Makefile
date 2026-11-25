PORT ?= 4173

.PHONY: dev
dev:
	@printf 'Home: http://127.0.0.1:%s/\nMental Arithmetic: http://127.0.0.1:%s/programs/mental-arithmetic/\n' $(PORT) $(PORT)
	@ruby -run -e httpd -- -b 127.0.0.1 -p $(PORT) ready-for-develop
