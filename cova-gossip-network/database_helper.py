from pydblite.pydblite import Base


class MemoryQueue(object):
    
    def __init__(self, name = "", col_names = ['col']):
        self.db = Base(name, save_to_file = False)
        self.db.create(*col_names)
        self.st = 0
        self.en = 0

    def pop(self):

        if(self.st == self.en):
            print('Queue Empty')

        ret = self.db[self.st]

        del self.db[self.st]
        self.st += 1

        return ret

    def top(self):

        if(self.st == self.en):
            print('Queue Empty')

        ret = self.db[self.st]

        return ret

    def push(self, arg = ['']):
        
        self.db.insert(*arg)
        self.en += 1

    def print_queue(self):

        for r in self.db:
            print(r)

    def is_empty(self):
        return self.st == self.en


class MemoryDict(object):

    def __init__(self, name = "", key = "", value = ['col']):

        self.db = Base(name, save_to_file = False)
        self.db.create(key, *value)
        self.db.create_index(key)
        self.key = key
        self.value = value

    def give_me_elem(self, key):
        return eval('self.db._' + self.key + '[key]')

    def is_in(self, key):
        return len(self.give_me_elem(key)) > 0

    def insert(self, key = "", value = [""]):

        record = self.give_me_elem(key)

        if len(record) > 0:
            for i in range(len(self.value)):
                record[0][self.value[i]] = value[i]
        else:
            self.db.insert(key, *value)

    def pop(self, key):
        record = self.give_me_elem(key)

        if len(record) > 0:
            rec_id = record[0]['__id__']
            del self.db[rec_id]

    def iteritems(self):
        return list(self.db)

    def len(self):
        return len(self.db)

    def print_all(self):

        for r in self.db:
            print(r)