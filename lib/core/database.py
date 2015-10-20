# This file is part of Viper - https://github.com/viper-framework/viper
# See the file 'LICENSE' for copying permission.

from __future__ import unicode_literals  # make all strings unicode in python2
from datetime import datetime

import psycopg2
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError

from lib.common.out import *
from lib.common.objects import File, Singleton
from lib.core.investigation import __project__

from os import path
Base = declarative_base()

association_table = Table(
    'association',
    Base.metadata,
    Column('tag_id', Integer, ForeignKey('tag.id')),
    Column('malware_id', Integer, ForeignKey('malware.id'))
)

malware_investigation = Table(
    'malware_investigation',
    Base.metadata,
    Column('investigation_id', Integer, ForeignKey('investigation.id')),
    Column('malware_id', Integer, ForeignKey('malware.id'))
)

DB_USER = 'admin'
DB_PASSWD = 'admin'

class Malware(Base):
    __tablename__ = 'malware'

    id = Column(Integer(), primary_key=True)
    name = Column(String(255), nullable=True)
    size = Column(Integer(), nullable=False)
    type = Column(Text(), nullable=True)
    mime = Column(String(255), nullable=True)
    md5 = Column(String(32), nullable=False, index=True)
    crc32 = Column(String(8), nullable=False)
    sha1 = Column(String(40), nullable=False)
    sha256 = Column(String(64), nullable=False, index=True)
    sha512 = Column(String(128), nullable=False)
    ssdeep = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=False), default=datetime.now(), nullable=False)
    tag = relationship(
        'Tag',
        secondary=association_table,
        backref=backref('malware')
    )
    investigation = relationship(
        'Investigation',
        secondary=malware_investigation,
        backref=backref('malware')
    )

    __table_args__ = (Index(
        'hash_index',
        'md5',
        'crc32',
        'sha1',
        'sha256',
        'sha512',
        unique=True
    ),)

    def to_dict(self):
        row_dict = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            row_dict[column.name] = value

        return row_dict

    def __repr__(self):
        return "<Malware('{0}','{1}')>".format(self.id, self.md5)

    def __init__(self,
                 md5,
                 crc32,
                 sha1,
                 sha256,
                 sha512,
                 size,
                 type=None,
                 mime=None,
                 ssdeep=None,
                 name=None):
        self.md5 = md5
        self.sha1 = sha1
        self.crc32 = crc32
        self.sha256 = sha256
        self.sha512 = sha512
        self.size = size
        self.type = type
        self.mime = mime
        self.ssdeep = ssdeep
        self.name = name


class Note(Base):
    __tablename__ = 'note'

    id = Column(Integer(), primary_key=True)
    title = Column(String(255), nullable=True)
    body = Column(Text(), nullable=False)

    def to_dict(self):
        row_dict = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            row_dict[column.name] = value

        return row_dict

    def __repr__(self):
        return "<Note ('{0}','{1}'>".format(self.id, self.title)

    def __init__(self, title, body):
        self.title = title
        self.body = body


class Tag(Base):
    __tablename__ = 'tag'

    id = Column(Integer(), primary_key=True)
    tag = Column(String(255), nullable=False, unique=True, index=True)

    def to_dict(self):
        row_dict = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            row_dict[column.name] = value

        return row_dict

    def __repr__(self):
        return "<Tag ('{0}','{1}'>".format(self.id, self.tag)

    def __init__(self, tag):
        self.tag = tag


class Investigation(Base):
    __tablename__ = 'investigation'

    id = Column(Integer(), primary_key=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    projectpath = Column(String(255), nullable=False, unique=True)

    def to_dict(self):
        row_dict = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            row_dict[column.name] = value

        return row_dict

    def __repr__(self):
        return "<Investigation ('{0}','{1}'>".format(self.id, self.name)

    def __init__(self, name, projectpath):
        self.name = name
        self.projectpath = projectpath


class Token(Base):
    __tablename__ = 'token'

    id = Column(Integer(), primary_key=True)
    user = Column(String(255), nullable=True, unique=False, index=True)
    apitoken = Column(String(255), nullable=False, unique=True, index=True)
    fqdn = Column(String(255), nullable=True, unique=False, index=True)
    app = Column(String(255), nullable=False, unique=False, index=True)

    def to_dict(self):
        row_dict = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            row_dict[column.name] = value

        return row_dict

    def __repr__(self):
        return "<Token ('{0}','{1}'>".format(self.id, self.name)

    def __init__(self, user, apitoken, fqdn, app):
        self.app = app
        self.apitoken = apitoken
        self.fqdn = fqdn
        self.user = user


class Database:
    metaclass_ = Singleton

    def __init__(self):
        if __project__.name is None:
            DB_NAME = 'default.db'
            db_path = path.join(__project__.get_path(), DB_NAME)
        else:
            DB_NAME = __project__.name + '.db'
            db_path = path.join(__project__.get_path(), DB_NAME)

        # Connect to Postgres DB
        self.engine = create_engine('postgresql+psycopg2://{0}:{1}!@localhost/cirtkit'.format(DB_USER, DB_PASSWD))

        self.engine.echo = False
        self.engine.pool_timeout = 60

        try:
            Base.metadata.create_all(self.engine)
        except OperationalError:
            # Connect to local SQLite DB if cannot connect to Postgres
            self.engine = create_engine('sqlite:///{0}'.format(db_path), poolclass=NullPool)
            Base.metadata.create_all(self.engine)

        self.Session = sessionmaker(bind=self.engine)

    def __del__(self):
        self.engine.dispose()

    # ############### TAG FUNCTIONS ################

    def add_tags(self, sha256, tags):
        session = self.Session()

        malware_entry = session.query(Malware).filter(Malware.sha256 == sha256).first()
        if not malware_entry:
            return

        tags = tags.strip()
        if ',' in tags:
            tags = tags.split(',')
        else:
            tags = tags.split()

        for tag in tags:
            tag = tag.strip().lower()
            if tag == '':
                continue

            try:
                malware_entry.tag.append(Tag(tag))
                session.commit()
            except IntegrityError as e:
                session.rollback()
                try:
                    malware_entry.tag.append(session.query(Tag).filter(Tag.tag==tag).first())
                    session.commit()
                except SQLAlchemyError:
                    session.rollback()

    def list_tags(self):
        session = self.Session()
        rows = session.query(Tag).all()
        return rows

    def delete_tag(self, tag_name, sha256):
        session = self.Session()
        
        try:
            # First remove the tag from the sample
            malware_entry = session.query(Malware).filter(Malware.sha256 == sha256).first()
            tag = session.query(Tag).filter(Tag.tag==tag_name).first()
            try:
                malware_entry = session.query(Malware).filter(Malware.sha256 == sha256).first()
                malware_entry.tag.remove(tag)
                session.commit()
            except:
                print_error("Tag {0} does not exist for this sample".format(tag_name))
            
            # If tag has no entries drop it
            count = len(self.find('tag', tag_name))
            if count == 0:
                session.delete(tag)
                session.commit()
                print_warning("Tag {0} has no additional entries dropping from Database".format(tag_name))
        except SQLAlchemyError as e:
            print_error("Unable to delete tag: {0}".format(e))
            session.rollback()
        finally:
            session.close()

    # ############### INVESTIGATION FUNCTIONS ################

    def add_investigation(self):
        session = self.Session()

        investigationName = ''
        investigationPath = ''

        if __project__.name:
            investigationName = __project__.name
            investigationPath = __project__.path
        else:
            print_error("Error. Not currently in an investigation context")
            return

        try:
            new_investigation = Investigation(name=investigationName,
                                              projectpath=investigationPath)
            session.add(new_investigation)
            session.commit()
        except IntegrityError:
            # Investigation probably already exists
            session.rollback()

    def remove_investigation(self, investid):
        session = self.Session()

        # retrieve id of investigation by name
        try:
            invest = session.query(Investigation).get(investid)
            if not invest:
                print_error("No investigation holds that id in the database.")
                return

            # if investigation found, delete it
            session.delete(invest)
            session.commit()
        except SQLAlchemyError as e:
            # check for errors deleting the investigation
            print_error("Unable to delete investigation: {0}".format(e))
            session.rollback()
            return False
        finally:
            session.close()

        return True

    def get_investigation_path(self, investid):
        session = self.Session()

        try:
            investigation = session.query(Investigation).get(investid)
            investpath = investigation.projectpath
            return investpath
        except SQLAlchemyError as e:
            print_error("Cannot locate investigation with ID: {0}".format(e))
            return None

    def get_investigation_list(self):
        session = self.Session()
        rows = session.query(Investigation).order_by(Investigation.id.desc())
        return rows

    # ############### MALWARE SAMPLE FUNCTIONS ################

    def add(self, obj, name=None, tags=None):
        session = self.Session()

        if not name:
            name = obj.name

        if isinstance(obj, File):
            try:
                malware_entry = Malware(md5=obj.md5,
                                        crc32=obj.crc32,
                                        sha1=obj.sha1,
                                        sha256=obj.sha256,
                                        sha512=obj.sha512,
                                        size=obj.size,
                                        type=obj.type,
                                        mime=obj.mime,
                                        ssdeep=obj.ssdeep,
                                        name=name)
                session.add(malware_entry)
                session.commit()
            except IntegrityError:
                session.rollback()
                malware_entry = session.query(Malware).filter(Malware.md5 == obj.md5).first()
            except SQLAlchemyError as e:
                print_error("Unable to store file: {0}".format(e))
                session.rollback()
                return False

        if tags:
            self.add_tags(sha256=obj.sha256, tags=tags)

        return True

    def delete_file(self, id):
        session = self.Session()

        try:
            malware = session.query(Malware).get(id)
            if not malware:
                print_error("The opened file doesn't appear to be in the database, have you stored it yet?")
                return

            session.delete(malware)
            session.commit()
        except SQLAlchemyError as e:
            print_error("Unable to delete file: {0}".format(e))
            session.rollback()
            return False
        finally:
            session.close()

        return True

    def find(self, key, value=None, offset=0):
        session = self.Session()
        offset = int(offset)
        rows = None

        if key == 'all':
            rows = session.query(Malware).all()
        elif key == 'latest':
            if value:
                try:
                    value = int(value)
                except ValueError:
                    print_error("You need to specify a valid number as a limit for your query")
                    return None
            else:
                value = 5
            
            rows = session.query(Malware).order_by(Malware.id.desc()).limit(value).offset(offset)
        elif key == 'md5':
            rows = session.query(Malware).filter(Malware.md5 == value).all()
        elif key == 'sha1':
            rows = session.query(Malware).filter(Malware.sha1 == value).all()
        elif key == 'sha256':
            rows = session.query(Malware).filter(Malware.sha256 == value).all()
        elif key == 'tag':
            rows = session.query(Malware).filter(Malware.tag.any(Tag.tag == value.lower())).all()
        elif key == 'name':
            if '*' in value:
                value = value.replace('*', '%')
            else:
                value = '%{0}%'.format(value)

            rows = session.query(Malware).filter(Malware.name.like(value)).all()
        elif key == 'type':
            rows = session.query(Malware).filter(Malware.type.like('%{0}%'.format(value))).all()
        elif key == 'mime':
            rows = session.query(Malware).filter(Malware.mime.like('%{0}%'.format(value))).all()
        else:
            print_error("No valid term specified")

        return rows

    # ############### GET COUNT FUNCTIONS ################
        
    def get_sample_count(self):
        session = self.Session()
        return session.query(Malware.id).count()

    def get_investigation_count(self):
        session = self.Session()
        return session.query(Investigation.id).count()

    # ############### NOTE FUNCTIONS ################

    def add_note(self, sha256, title, body):
        session = self.Session()

        malware_entry = session.query(Malware).filter(Malware.sha256 == sha256).first()
        if not malware_entry:
            return

        try:
            malware_entry.note.append(Note(title, body))
            session.commit()
        except SQLAlchemyError as e:
            print_error("Unable to add note: {0}".format(e))
            session.rollback()
        finally:
            session.close()

    def get_note(self, note_id):
        session = self.Session()
        note = session.query(Note).get(note_id)
        return note

    def edit_note(self, note_id, body):
        session = self.Session()

        try:
            session.query(Note).get(note_id).body = body
            session.commit()
        except SQLAlchemyError as e:
            print_error("Unable to update note: {0}".format(e))
            session.rollback()
        finally:
            session.close()

    def delete_note(self, note_id):
        session = self.Session()

        try:
            note = session.query(Note).get(note_id)
            session.delete(note)
            session.commit()
        except SQLAlchemyError as e:
            print_error("Unable to delete note: {0}".format(e))
            session.rollback()
        finally:
            session.close()

    # ############### TOKEN FUNCTIONS ################

    def get_token_list(self):
        session = self.Session()
        rows = session.query(Token).order_by(Token.id.desc())
        return rows

    def add_token(self, newtoken, username, app, hostname):
        session = self.Session()

        token_entry = session.query(Token).filter(Token.apitoken == newtoken).first()
        if token_entry:
            username = token_entry.user
            print_error("Token already stored under username: {0}".format(username))
            return

        try:
            new_token = Token(app=app,
                              apitoken=newtoken,
                              fqdn=hostname,
                              user=username)
            session.add(new_token)
            session.commit()
        except SQLAlchemyError as e:
            print_error("Unable to add token: {0}".format(e))
            session.rollback()
        finally:
            session.close()

    def delete_token(self, token_id):
        session = self.Session()

        try:
            token = session.query(Token).get(token_id)
            session.delete(token)
            session.commit()
        except SQLAlchemyError as e:
            print_error("Unable to delete token: {0}".format(e))
            session.rollback()
        finally:
            session.close()
