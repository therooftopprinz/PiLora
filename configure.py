#!/usr/bin/python
import os
import sys
import subprocess

CXX      = 'g++'
AR       = 'ar'
MAKE     = 'make'
CXXFLAGS = '-std=c++17 -O0 -ggdb3 -Wall -Werror'

TLD = os.path.dirname(sys.argv[0])+'/'
PWD = os.getcwd()+'/'

class Build:
    def __init__(self):
        self.input_files = []
        self.output_file = ''
        self.src_dir = ''
        self.dependencies = []
        self.external_dependencies = []
        self.target_type = 0
        self.cxxflags = ''
        self.linkflags = ''
    def add_include_paths(self, p):
        self.cxxflags = self.cxxflags + ' ' +' '.join(['-I'+TLD+i for i in p])
    def set_cxxflags(self, f):
        self.cxxflags = f
    def set_linkflags(self, f):
        self.linkflags = f
    def set_src_dir(self, d):
        self.src_dir = TLD+d
    def add_src_files(self, f):
        self.name = f
        self.input_files.extend(f)
    def target_executable(self, f):
        self.name = f +"_build"
        self.output_file = f
        self.target_type = 0
    def target_archive(self, f):
        self.name = f +"_build"
        self.output_file = f
        self.target_type = 1
    def add_dependencies(self, d):
        self.dependencies.extend(d)
    def add_external_dependencies(self, d):
        self.external_dependencies.extend(d)
    def generate_make(self):
        output = ''
        objects = [self.name+'/'+i+'.o' for i in self.input_files]
        deps    = [self.name+'/'+i+'.d' for i in self.input_files]
        srcs    = [self.src_dir+i for i in self.input_files]
        print objects
        print deps
        print srcs
        output = output + '-include '+' '.join(deps) + '\n'
        output = output + self.output_file + ':' + ' '.join(self.dependencies)+' '+' '.join(objects) + '\n'
        # target rule
        if (self.target_type == 0):
            output = output + '\t'+ CXX + ' ' + ' '.join(objects) + ' ' + ' '.join(self.dependencies) + ' ' + ' '.join([TLD+i for i in self.external_dependencies]) + ' ' + self.linkflags +  ' -o ' + self.output_file + '\n'
        else:
            output = output + '\t'+ AR + ' rcs ' + self.linkflags + ' ' + self.output_file + ' ' + ' '.join(objects) + '\n'

        # object rule
        for i in range(len(self.input_files)):
            output = output + objects[i] + ':' + srcs[i] + '\n'
            output = output +'\t@mkdir -p ' + os.path.dirname(objects[i]) + '\n'
            output = output +'\t@echo Building '+objects[i]+'..\n'
            output = output +'\t@'+ CXX + ' -MMD ' + self.cxxflags + ' -c ' + srcs[i] + ' -o ' + objects[i] + '\n'

        return output;

def clean_filenames(a):
    return [i.strip().replace('./','') for i in a]

print 'configuring for testing'

print 'TLD is ' + TLD
print 'PWD is ' + PWD

TEST_SOURCES = []
SRC_SOURCES  = []
STUB_SOURCES  = []

p = subprocess.Popen('cd '+TLD+'test        && find .             | egrep \'\.cpp$\'', shell=True, stdout=subprocess.PIPE)
q = subprocess.Popen('cd '+TLD+'src         && find .             | egrep \'\.cpp$\' | grep -v main.cpp', shell=True, stdout=subprocess.PIPE)
r = subprocess.Popen('cd '+TLD+'HwApiStub   && find .             | egrep \'\.cpp$\' | grep -v main.cpp', shell=True, stdout=subprocess.PIPE)
s = subprocess.Popen('cd '+TLD+'common      && find .             | egrep \'\.cpp$\' | grep -v main.cpp', shell=True, stdout=subprocess.PIPE)
u = subprocess.Popen('cd '+TLD+'PigpioHwApi && find .             | egrep \'\.cpp$\' | grep -v main.cpp', shell=True, stdout=subprocess.PIPE)

TEST_SOURCES = clean_filenames(p.stdout.readlines())
SRC_SOURCES  = clean_filenames(q.stdout.readlines())
STUB_SOURCES  = clean_filenames(r.stdout.readlines())
COMMON_SOURCES  = clean_filenames(s.stdout.readlines())
PIGPIO_SOURCES  = clean_filenames(u.stdout.readlines())


print "TEST_SOURCES", TEST_SOURCES
print "SRC_SOURCES", SRC_SOURCES
print "SRC_SOURCES", STUB_SOURCES
print "COMMON_SOURCES", COMMON_SOURCES
print "PIGPIO_SOURCES", PIGPIO_SOURCES

gtest = Build()
gtest.set_cxxflags(CXXFLAGS)
gtest.set_src_dir('gtest/')
gtest.add_src_files(['gmock-gtest-all.cc'])
gtest.add_include_paths(['gtest'])
gtest.target_archive('gtest.a')

src = Build()
src.set_cxxflags(CXXFLAGS)
src.add_include_paths(['src/', 'HwApi/', 'common/', 'Logless/src/'])
src.set_src_dir('src/')
src.add_src_files(SRC_SOURCES)
src.target_archive('src.a')

common = Build()
common.set_cxxflags(CXXFLAGS)
common.add_include_paths(['common/'])
common.set_src_dir('common/')
common.add_src_files(COMMON_SOURCES)
common.target_archive('common.a')

pigpiohwApi = Build()
pigpiohwApi.set_cxxflags(CXXFLAGS)
pigpiohwApi.add_include_paths(['HwApi/', 'common/', 'src/', 'Logless/src/'])
pigpiohwApi.set_src_dir('PigpioHwApi/')
pigpiohwApi.add_src_files(PIGPIO_SOURCES)
pigpiohwApi.target_archive('pigpiohwapi.a')

hwapistub = Build()
hwapistub.set_cxxflags(CXXFLAGS)
hwapistub.add_include_paths(['HwApi/', 'common/', 'src/', 'Logless/src/'])
hwapistub.set_src_dir('HwApiStub/')
hwapistub.add_src_files(STUB_SOURCES)
hwapistub.target_archive('stub.a')

test = Build()
test.set_cxxflags(CXXFLAGS)
test.add_include_paths(['gtest/', 'src/', 'HwApi/', 'test/', 'common/', 'Logless/src/'])
test.set_src_dir('test/')
test.add_src_files(TEST_SOURCES)
test.add_dependencies(['gtest.a', 'src.a', 'common.a'])
test.add_external_dependencies(['Logless/build/logless.a'])
test.set_linkflags("-lpthread")
test.target_executable('test')

binstub = Build()
binstub.set_cxxflags(CXXFLAGS)
binstub.add_include_paths(['src/', 'HwApi/', 'common/', 'Logless/src/'])
binstub.set_src_dir('src/')
binstub.add_src_files(["main.cpp"])
binstub.add_dependencies(['src.a', 'stub.a', 'common.a'])
binstub.add_external_dependencies(['Logless/build/logless.a'])
binstub.set_linkflags("-lpthread")
binstub.target_executable('binstub')

binpigpio = Build()
binpigpio.set_cxxflags(CXXFLAGS)
binpigpio.add_include_paths(['src/', 'HwApi/', 'HwApi/', 'common/', 'Logless/src/'])
binpigpio.set_src_dir('src/')
binpigpio.add_src_files(["main.cpp"])
binpigpio.add_dependencies(['src.a', 'pigpiohwapi.a', 'common.a'])
binpigpio.add_external_dependencies(['Logless/build/logless.a'])
binpigpio.set_linkflags("-lpthread -lpigpiod_if2")
binpigpio.target_executable('binpigpio')

with open('Makefile','w+') as mf:
    mf.write(gtest.generate_make())
    mf.write(test.generate_make())
    mf.write(src.generate_make())
    mf.write(common.generate_make())
    mf.write(pigpiohwApi.generate_make())
    mf.write(hwapistub.generate_make())
    mf.write(binstub.generate_make())
    mf.write(binpigpio.generate_make())