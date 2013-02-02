#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This utility takes a already processed articles
# and create a new file with part of these articles based in
# ignoring the articles in a list

import codecs
import os
import config
from make_selection import FileListReader, RedirectParser, RedirectsUsedWriter
from make_selection import CountedTemplatesReader, normalize_title
if __name__ == '__main__':

    input_xml_file_name = config.input_xml_file_name

    print "Loading low rank pages"
    ignored_pages_reader = FileListReader('%s.low_rank_pages' %
            input_xml_file_name)

    processed_file = open("%s.processed" % input_xml_file_name, mode='r')
    output_file = open("%s.processed_filtered" % input_xml_file_name, mode='w')


    data_line = processed_file.readline()
    while data_line:
        #print data_line
        if len(data_line) == 2:
            if ord(data_line[0]) == 1:
                title = processed_file.readline()
                # read article size
                # size
                size_line = processed_file.readline()
                # \02
                data_line = processed_file.readline()
                title = normalize_title(title[0:-1])
                if title not in ignored_pages_reader.list:

                    # \01
                    output_file.write('\01\n')
                    output_file.write('%s\n' % title)
                    # size
                    output_file.write('%s\n' % size_line)
                    # \02
                    output_file.write('\02\n')
                    finish = False
                    while not finish:
                        line = processed_file.readline()
                        output_file.write('%s\n' % line)
                        if len(line) == 2:
                            if ord(line[0]) == 3:
                                output_file.write('\03\n')
                                finish = True
                                break
                else:
                    print "* Ignored %s " % title

        data_line = processed_file.readline()

    output_file.close()

    # clean redirects used
    print "Loading redirects used "
    redirect_checker = RedirectParser(input_xml_file_name,
            postfix='redirects_used')

    print "Loading selected pages"
    selected_pages_reader = FileListReader('%s.pages_selected-level-1' %
            input_xml_file_name)

    print "Cleaning selected pages list"
    # clean selected_pages_reader list
    filtered_list = []
    for article in selected_pages_reader.list:
        if article not in ignored_pages_reader.list:
            filtered_list.append(article)

    print "Loading templates used"
    templates_used_reader = CountedTemplatesReader(input_xml_file_name)

    print "Writing redirects used filtered"
    redirect_writer = RedirectsUsedWriter(input_xml_file_name, filtered_list,
            templates_used_reader.templates,
            redirect_checker, postfix='redirects_used_filtered')
