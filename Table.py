from prettytable import PrettyTable
from random import randint
import random
from string import ascii_lowercase
from copy import deepcopy
import names
lower_ID = 100
upper_ID = 999
colors = ['white', 'green', 'purple', 'black', 'blue', 'yellow', 'red', 'orange']
color = "color"
ID = "ID"
first = "first"
last = "last"
def dict_to_list(d):
    return [(k, v) for k, v in d.items()] 
    

def And(lis):
    return all(lis)

def Or(lis):
    return any(lis)

def st(a,b):
    return a < b
def ste(a,b):
    return a <= b
def gt(a,b):
    return a > b
def gte (a,b):
    return a >= b
def eq(a,b):
    return a == b
def neq(a,b):
    return a != b

def remove_additions(column):
    return column[column.rfind('.')+1:].rstrip("12")

def remove_dups(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]

def set_ID_lims(lower, upper):
    global lower_ID, upper_ID
    lower_ID = lower
    upper_ID = upper

def rand_float(num = 100):
    return round(random.random()* num,2) 
def rand_int(num = 100):
    return random.randint(0,num)
def rand_str(length = 4):
    return ''.join(random.choice(ascii_lowercase) for i in range(length))
def rand_id():
    return random.randint(lower_ID,upper_ID)
def rand_color():
    return random.choice(colors)

rand_dict = {int: rand_int, float:rand_float, str:rand_str,\
             'first':names.get_first_name, 'last':names.get_last_name,\
             'ID': rand_id, 'color':rand_color}    

symbol_dict = {And:'∧', Or:'∨',\
               '<':st, '<=':ste,\
               '>':gt, '>=':gte,\
               '=':eq, '!=':neq}


class Condition:
    def check(self): pass
    def __str__(self): pass

class cond_v(Condition):
    def __init__(self, schema_col = "", func_symb = None, val = 0):
        self.schema_col = schema_col
        self.func_symb = func_symb
        self.val = val
    def check(self, tab_instance):
        if self.schema_col not in tab_instance:
            print("irrelevant condition")
        return symbol_dict[self.func_symb](tab_instance[self.schema_col],self.val)
    def __str__(self):
        return self.schema_col + self.func_symb + str(self.val)
        

class cond_c(Condition):
    def __init__(self, schema_col1 = "", func_symb = None, schema_col2 = 0):
        self.schema_col1 = schema_col1
        self.func_symb = func_symb
        self.schema_col2 = schema_col2
    def check(self, tab_instance):
        if self.schema_col1 not in tab_instance or self.schema_col2 not in tab_instance:
            print("irrelevant condition")
            return False
        return symbol_dict[self.func_symb](tab_instance[self.schema_col1],tab_instance[self.schema_col2]) 
    def __str__(self):
        return self.schema_col1 + self.func_symb + self.schema_col2     
            
class cond_p(Condition):
    def __init__(self, logic, *conditions):
        self.condition_list = conditions
        self.logic = logic
    def add_conditions(self, *conditions):
        for cond in conditions:
            self.condition_list.append(cond)
    def check(self, tab_instance):
        return self.logic([cond.check(tab_instance) for cond in self.condition_list])
    def __str__(self):
        return '(' + symbol_dict[self.logic].join([str(cond) for cond in self.condition_list]) + ')'

class Table:

    def __init__(self, name, *argv):
        self.instances = []
        self.schema = argv
        self.PT = PrettyTable()
        self.name = name
        self.PT.field_names = list(argv)
        self.schem_dups = []

    def add(self, **kwargs):
        if tuple(kwargs.keys()) != self.schema:
            print("does not match schema")
            return
        instance = kwargs
        if instance in self.instances:
            return 
        self.instances.append(instance)
        self.PT.add_row(list(instance.values()))
        return

    def randomize(self, num, **kwargs):
        if tuple(kwargs.keys()) != self.schema:
            print("does not match schema")
            return
        for i in range(num):
            instance = deepcopy(kwargs)
            for key in instance.keys():
                instance[key] = rand_dict[instance[key]]()
            self.add(**instance)    

    def print(self):
        print("Table {0}:".format(self.name))
        print(self.PT)
        print()



    #Operators


    def project(self, *argv):
        indexes = []
        for arg in argv:
            if arg not in self.schema:
                print("unmatching schema")
                return
            else:
                indexes.append(self.schema.index(arg))
        new_schema = [self.schema[index] for index in indexes]
        ret_tab = Table("π({0}){1}".format(', '.join(new_schema), self.name), *new_schema)
        for instance in self.instances:
            new_instance = {self.schema[i]:list(instance.values())[i] for i in indexes}
            ret_tab.add(**new_instance)
        return ret_tab

    def rename(self, *argv):
        if len(argv) != len(self.schema):
            print("unmatching schema lengths")
            return
        print()
        ret_tab = Table("ρ({0}){1}".format(', '.join(argv), self.name), *argv)
        for instance in self.instances:
            new_instance = dict(zip(argv, instance.values()))
            ret_tab.add(**new_instance)
        return ret_tab

    def union(self, other):
        if self.schema != other.schema:
            print("unmatching schema")
            return
        ret_tab = Table("{0}∪{1}".format(self.name, other.name), *self.schema)
        for instance in self.instances:
            ret_tab.add(**instance)
        for instance in other.instances:
            ret_tab.add(**instance)
        return ret_tab

    def select(self, condition):
        ret_tab = Table("σ({0}){1}".format(condition, self.name), *self.schema)
        for instance in self.instances:
            if condition.check(instance):
                ret_tab.add(**instance)
        return ret_tab

    def difference(self, other):
        if self.schema != other.schema:
            print("unmatching schema")
            return
        ret_tab = Table("{0}-{1}".format(self.name, other.name), *self.schema)
        for instance in self.instances:
            if instance not in other.instances:
                ret_tab.add(**instance)
        return ret_tab


    def cart_prod(self, other):
        new_self_schema = list(self.schema)
        new_other_schema = list(other.schema)
        self_fmt = self.name + ".{}"
        other_fmt = other.name + ".{}"
        if self.name == other.name:
            self_fmt = "{}1"
            other_fmt = "{}2"
        schem_dups = []
        for i in range(len(new_other_schema)):
            for j in range(len(new_self_schema)):
                if new_other_schema[i] == new_self_schema[j]:
                    schem_dups.append(new_other_schema[i])
                    new_other_schema[i] = other_fmt.format(new_other_schema[i])
                    new_self_schema[j] = self_fmt.format(new_self_schema[j])
        ret_tab = Table("{0}⨯{1}".format(self.name, other.name), *(new_self_schema + new_other_schema))
        new_instances = [dict(list(zip(new_self_schema, inst_1.values()))+list(zip(new_other_schema, inst_2.values()))) for inst_1 in self.instances for inst_2 in other.instances]
        for instance in new_instances:
            ret_tab.add(**instance)
        ret_tab.schem_dups = schem_dups
        return ret_tab


    def intersection(self, other):
        if self.schema != other.schema:
            print("unmatching schema")
            return
        ret_tab = Table("intersection {0}∩{1}".format(self.name, other.name), *self.schema)
        for instance in self.instances:
            if instance in other.instances:
                ret_tab.add(**instance)
        return ret_tab

    def cond_join(self, other, condition):
        ret_tab = self.cart_prod(other).select(condition)
        ret_tab.name = "{0}⨝({2}){1}".format(self.name, other.name, condition)
        return ret_tab

    def natural_join(self, other):
        cp = self.cart_prod(other)
        new_schema = remove_dups([remove_additions(col) for col in cp.schema])
        dup_groups = [[i for i in cp.schema if i.startswith(dup) or i.endswith('.'+dup)] for dup in cp.schem_dups]
        ret_tab = Table("{0}⨝{1}".format(self.name, other.name), *new_schema)
        for instance in cp.instances:
            valid = True
            for group in dup_groups:
                for dup_i in range(len(group)-1):
                    if instance[group[dup_i]] != instance[group[dup_i+1]]:
                        valid = False
            if valid == True:
                new_instance = dict([(remove_additions(i[0]),i[1]) for i in dict_to_list(instance) if remove_additions(i[0]) in new_schema])
                ret_tab.add(**new_instance)
        return ret_tab

    def division(self, other):
        if not set(other.schema) <= set(self.schema):
            print("incompatible schema")
            return
        new_schema = [col for col in self.schema if col not in other.schema]
        ret_tab = Table("{0}÷{1}".format(self.name, other.name), *new_schema)
        for self_inst in self.instances:
            for other_inst in other.instances:
                valid = True
                for key in other_inst.keys():
                    if self_inst[key] != other_inst[key]:
                        valid = False
            if valid == True:
                new_instance = dict([i for i in dict_to_list(self_inst) if i[0] in new_schema])
                ret_tab.add(**new_instance)
        
        return ret_tab     
    



        




