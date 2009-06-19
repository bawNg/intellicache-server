#!/usr/bin/env python

from elixir import *
import config

metadata.bind = "mysql://%s:%s@%s/%s" % (config.mysql_username, config.mysql_password, config.mysql_address, config.mysql_database)
metadata.bind.echo = True

class Server(Entity):
	using_options(tablename='servers')
	name	= Field(Text)
	address	= Field(Text)
	nzbs	= OneToMany('Nzb')

	def __repr__(self): return '<Server "%s">' % (self.name)

class Nzb(Entity):
	using_options(tablename='nzbs')
	name		= Field(Text)
	unique_id	= Field(Text)
	date_added	= Field(DateTime)
	server		= ManyToOne('Server')
	files		= OneToMany('File')

	def __repr__(self): return '<Nzb "%s">' % (self.name)

class File(Entity):
	using_options(tablename='files')
	subject		= Field(Text)
	articles	= OneToMany('Article')
	nzb			= ManyToOne('Nzb')

	def __repr__(self): return '<File "%s">' % (self.name)

class Article(Entity):
	using_options(tablename='articles')
	message_id		= Field(Text)
	size			= Field(Integer)
	file			= ManyToOne('File')
	is_cached		= Field(Boolean)
	time_cached 	= Field(DateTime)
	is_being_cached	= Field(Boolean)
	being_cached_by = ManyToMany('User', tablename='articles_being_cached_by')

	def __repr__(self): return '<Article "%s">' % (self.name)

class User(Entity):
	using_options(tablename='users')
	name = Field(Text)
	is_online = Field(Boolean)
	articles_caching = ManyToMany('Article', tablename='articles_being_cached_by')

	def __repr__(self): return '<User "%s">' % (self.name)

setup_all()