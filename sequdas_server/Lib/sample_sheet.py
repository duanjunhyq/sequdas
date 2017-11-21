import os
import re
from os import path, listdir
from csv import reader
from collections import OrderedDict
import json
from copy import deepcopy

def get_csv_reader(sample_sheet_file):

    """
    tries to create a csv.reader object which will be used to
        parse through the lines in SampleSheet.csv
    raises an error if:
            sample_sheet_file is not an existing file
            sample_sheet_file contains null byte(s)

    arguments:
            data_dir -- the directory that has SampleSheet.csv in it

    returns a csv.reader object
    """

    if path.isfile(sample_sheet_file):
        csv_file = open(sample_sheet_file, "rb")
        # strip any trailing newline characters from the end of the line
        # including Windows newline characters (\r\n)
        csv_lines = [x.rstrip('\n') for x in csv_file]
        csv_lines = [x.rstrip('\r') for x in csv_lines]

        # open and read file in binary then send it to be parsed by csv's
        # reader
        csv_reader = reader(csv_lines)
    else:
        msg = sample_sheet_file + " is not a valid SampleSheet file (it's"
        msg += "not a valid CSV file)."
        raise SampleSheetError(msg, ["SampleSheet.csv cannot be parsed as a CSV file because it's not a regular file."])

    return csv_reader
    
def parse_metadata(sample_sheet_file):

    """
    Parse all lines under [Header], [Reads] and [Settings] in .csv file
    Lines under [Reads] are stored in a list with key name "readLengths"
    All other key names are translated according to the
        metadata_key_translation_dict

    arguments:
            sample_sheet_file -- path to SampleSheet.csv

    returns a dictionary containing the parsed key:pair values from .csv file
    """

    metadata_dict = {}
    metadata_dict["readLengths"] = []

    csv_reader = get_csv_reader(sample_sheet_file)
    add_next_line_to_dict = False

    metadata_key_translation_dict = {
        'Assay': 'assay',
        'Description': 'description',
        'Application': 'application',
        'Investigator Name': 'investigatorName',
        'Adapter': 'adapter',
	    'AdapterRead2': 'adapterread2',
        'Workflow': 'workflow',
        'ReverseComplement': 'reversecomplement',
        'IEMFileVersion': 'iemfileversion',
        'Date': 'date',
        'Experiment Name': 'experimentName',
        'Chemistry': 'chemistry',
        'Project Name': 'projectName'
    }

    section = None

    for line in csv_reader:
        if "[Header]" in line or "[Settings]" in line:
            section = "header"
            continue
        elif "[Reads]" in line:
            section = "reads"
            continue
        elif "[Data]" in line:
            break
        elif line and line[0].startswith("["):
            section = "unknown"
            continue

        if not line or not line[0]:
            continue

        if not section:
            raise SampleSheetError("This sample sheet doesn't have any sections.", ["The sample sheet is missing important sections: no sections were found."])
        elif section is "header":
            try:
                key_name = metadata_key_translation_dict[line[0]]
                metadata_dict[key_name] = line[1]
            except KeyError:
                logging.info("Unexpected key in header: [{}]".format(line[0]))
        elif section is "reads":
            metadata_dict["readLengths"].append(line[0])

    # currently sends just the larger readLengths
    if len(metadata_dict["readLengths"]) > 0:
        if len(metadata_dict["readLengths"]) == 2:
            metadata_dict["layoutType"] = "PAIRED_END"
        else:
            metadata_dict["layoutType"] = "SINGLE_END"
        metadata_dict["readLengths"] = max(metadata_dict["readLengths"])
    else:
        # this is an exceptional case, you can't have no read lengths!
        raise SampleSheetError("Sample sheet must have read lengths!", ["The sample sheet is missing important sections: no [Reads] section found."])

    return metadata_dict

class Sample(object):

    def __init__(self, new_samp_dict, run=None, sample_number=None):
        self.sample_dict = dict(new_samp_dict)
        self.seq_file = None
        self._run = run
        self._sample_number = sample_number
        self._already_uploaded = False

    def get_id(self):
        # When pulling sample records from the server, the sample name *is* the
        # identifier for the sample, so if it's not specified in the dictionary
        # that we're using to build this sample, set it as the sample name that
        # we got from the server.
        try:
            return self.sample_dict["sequencerSampleId"]
        except KeyError:
            return self.sample_dict["sampleName"]

    @property
    def already_uploaded(self):
        return self._already_uploaded

    @already_uploaded.setter
    def already_uploaded(self, already_uploaded=False):
        self._already_uploaded = already_uploaded

    @property
    def sample_name(self):
        return self.get("sampleName")

    @property
    def sample_number(self):
        return self._sample_number

    def get_project_id(self):
        return self.get("sampleProject")

    def get_dict(self):
        return self.sample_dict

    def __getitem__(self, key):
        ret_val = None
        if key in self.sample_dict:
            ret_val = self.sample_dict[key]
        return ret_val

    def get(self, key):
        return self.__getitem__(key)

    def get_sample_metadata(self):
        return self.seq_file.get_properties()

    def get_files(self):
        return self.seq_file.get_files()

    def get_files_size(self):
        return self.seq_file.get_files_size()

    def set_seq_file(self, seq_file):
        self.seq_file = seq_file

    def is_paired_end(self):
        return len(self.seq_file.get_files()) == 2

    def __str__(self):
        return str(self.sample_dict) + str(self.seq_file)

    @property
    def upload_progress_topic(self):
        return self._run.upload_progress_topic + "." + self.get_id()

    @property
    def upload_started_topic(self):
        return self._run.upload_started_topic + "." + self.get_id()

    @property
    def upload_completed_topic(self):
        return self._run.upload_completed_topic + "." + self.get_id()

    @property
    def upload_failed_topic(self):
        return self._run.upload_failed_topic + "." + self.get_id()

    @property
    def online_validation_topic(self):
        return self._run.online_validation_topic + "." + self.get_id()

    @property
    def run(self):
        return self._run

    @run.setter
    def run(self, run):
        logging.info("Setting run.")
        self._run = run

    class JsonEncoder(json.JSONEncoder):

        def default(self, obj):

            if isinstance(obj, Sample):
                sample_dict = dict(obj.get_dict())
                # get sample dict and make a copy of it
                sample_dict.pop("sampleProject")
                if "sequencerSampleId" in sample_dict:
                    # if the sample ID field is populated, then we've just Finished
                    # reading the run from disk and we're preparing to send data
                    # to the server. The server is using the sample ID field as the
                    # name of the sample, so overwrite whatever we *were* using to
                    # find files with the sample ID field.
                    sample_dict["sampleName"] = sample_dict["sequencerSampleId"]
                return sample_dict
            else:
                return json.JSONEncoder.default(self, obj)

def parse_samples(sample_sheet_file):

    """
    Parse all the lines under "[Data]" in .csv file
    Keys in sample_key_translation_dict have their values changed for
        uploading to REST API
    All other keys keep the same name that they have in .csv file

    arguments:
            sample_sheet_file -- path to SampleSheet.csv

    returns	a list containing Sample objects that have been created by a
        dictionary from the parsed out key:pair values from .csv file
    """

    csv_reader = get_csv_reader(sample_sheet_file)
    # start with an ordered dictionary so that keys are ordered in the same
    # way that they are inserted.
    sample_dict = OrderedDict()
    sample_list = []

    sample_key_translation_dict = {
        'Sample_Name': 'sampleName',
        'Description': 'description',
        'Sample_ID': 'sequencerSampleId',
        'Sample_Project': 'sampleProject'
    }

    parse_samples.sample_key_translation_dict = sample_key_translation_dict

    # initilize dictionary keys from first line (data headers/attributes)
    set_attributes = False
    for line in csv_reader:

        if set_attributes:
            for item in line:

                if item in sample_key_translation_dict:
                    key_name = sample_key_translation_dict[item]
                else:
                    key_name = item

                sample_dict[key_name] = ""

            break

        if "[Data]" in line:
            set_attributes = True

    # fill in values for keys. line is currently below the [Data] headers
    for sample_number, line in enumerate(csv_reader):

        if len(sample_dict.keys()) != len(line):
            """
            if there is one more Data header compared to the length of
            data values then add an empty string to the end of data values
            i.e the Description will be empty string
            assumes the last Data header is going to be the Description
            this handles the case where the last trailing comma is trimmed

            Shaun said this issue may come up when a user edits the
            SampleSheet from within the MiSeq software
            """
            if len(sample_dict.keys()) - len(line) == 1:
                line.append("")
            else:
                raise SampleSheetError(
                    "Number of values doesn't match number of " +
                    "[Data] headers. " +
                    ("Number of [Data] headers: {data_len}. " +
                     "Number of values: {val_len}").format(
                        data_len=len(sample_dict.keys()),
                        val_len=len(line)
                    ), [("Your sample sheet is malformed. I expected to find {} "
                         "columns the [Data] section, but I only found {} columns "
                         "for line {}.".format(len(sample_dict.keys()), len(line), line))]
                )

        for index, key in enumerate(sample_dict.keys()):
            sample_dict[key] = line[index].strip()  # assumes values are never empty

        if len(sample_dict["sampleName"]) == 0:
            sample_dict["sampleName"] = sample_dict["sequencerSampleId"]

        sample = Sample(deepcopy(sample_dict), sample_number=sample_number+1)
        sample_list.append(sample)

    return sample_list


def parse_out_sequence_file(sample):

    """
    Removes keys in argument sample that are not in sample_keys and
        stores them in sequence_file_dict

    arguments:
            sample -- Sample object
            the dictionary inside the Sample object is changed

    returns a dictionary containing keys not in sample_keys to be used to
        create a SequenceFile object
    """

    sample_keys = ["sampleName", "description",
                   "sequencerSampleId", "sampleProject"]
    sequence_file_dict = {}
    sample_dict = sample.get_dict()
    for key in sample_dict.keys()[:]:  # iterate through a copy
        if key not in sample_keys:
            sequence_file_dict[key] = sample_dict[key]
            del sample_dict[key]

    return sequence_file_dict