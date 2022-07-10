# from distutils.log import WARN, debug
import argparse
import csv
import logging
import re
import sys
from datetime import datetime
from logging import debug, error, info
from typing import Dict, List, OrderedDict, Tuple

import requests
import yaml

BASE_CONFIGS = {
    "BASE_EXPORTER_YAML_PATH": "/Users/abhishek.walia/Documents/Codes/github/jmx-monitoring-stacks/shared-assets/jmx-exporter",
    "OUTPUT_CSV_PATH": "/Users/abhishek.walia/Documents/Codes/github/jmx-monitoring-stacks/utils/testing/output",
    "ZOOKEEPER_EXPORTER": "zookeeper.yml",
    "KAFKA_EXPORTER": "kafka_broker.yml",
    "CONNECT_EXPORTER": "kafka_connect.yml",
    "KSQLDB_EXPORTER": "confluent_ksql.yml",
    # This is required as Jolokia tries to parse various percentiles and rates as attributes whereas Prometheus parses them as either quantile or GAUGE for later aggregation
    "IGNORED_ATTR_LIST": ["50thpercentile", "75thpercentile", "95thpercentile", "98thpercentile", "999thpercentile", "99thpercentile", \
                          "max", "mean", "min", "stddev", 'eventtype', 'fifteenminuterate', 'fiveminuterate', 'oneminuterate', 'meanrate', 'rateunit', 'latencyunit', 'loggers'],
    "IGNORED_BEAN_LIST": ["org.eclipse.*", "org.apache.*", "jmx4per.*", "jmimpl.*", "jdk.management.*", "java.nio.*", "joloki.*", \
                          "java.lan.*", "com.sun.*", "log4.*", "sun.nio.*", "java.util.log.*"]
}

TRANSLATION_TABLE = {
    ".": "_",
    "-": "_",
    "_": "_",
}
SPLITTER = "~~~"

CALL_MAPPINGS = {
    "ZOOKEEPER": {
        "EXPORTER": "http://localhost:49900/",
        "JOLOKIA": "http://localhost:49901/",
        "CONFIG": "ZOOKEEPER_EXPORTER"
    },
    "KAFKA1": {
        "EXPORTER": "http://localhost:49910/",
        "JOLOKIA": "http://localhost:49911/",
        "CONFIG": "KAFKA_EXPORTER"
    },
    "KAFKA2": {
        "EXPORTER": "http://localhost:49920/",
        "JOLOKIA": "http://localhost:49921/",
        "CONFIG": "KAFKA_EXPORTER"
    },
    "CONNECT": {
        "EXPORTER": "http://localhost:49930/",
        "JOLOKIA": "http://localhost:49931/",
        "CONFIG": "CONNECT_EXPORTER"
    },
    "KSQLDB": {
        "EXPORTER": "http://localhost:49950/",
        "JOLOKIA": "http://localhost:49951/",
        "CONFIG": "KSQLDB_EXPORTER"
    },
}


def make_http_call(url: str):
    debug(f"Calling URL: {url}")
    resp = requests.get(url)
    debug(f"Response Code: {resp.status_code}")
    debug(f"Response Received: {resp}")
    return resp


def mbean_common_format(mbean_name: str, mbean_vars: List, mbean_attrs: List) -> List[str]:
    output_data = list()
    for attr_item in mbean_attrs:
        outstring = SPLITTER.join([mbean_name, SPLITTER.join(mbean_vars), attr_item]).lower().translate(TRANSLATION_TABLE)
        output_data.append(str(outstring.lower()))
    output_data.sort()
    return output_data


def jolokia_output_whitelist_blacklist(mbean_string_list: List, ):
    output_data = list()
    for item in mbean_string_list:
        in_item = str(item).lower()
        check_whitelist = True if re.fullmatch(instance_whitelist_pattern, in_item) is not None else False
        check_blacklist = True if re.fullmatch(instance_blacklist_pattern, in_item) is not None else False
        if check_whitelist and check_blacklist:
            pass
        elif check_whitelist and not check_blacklist:
            output_data.append(str(in_item))
        elif not check_whitelist and check_blacklist:
            pass
        elif not check_whitelist and not check_blacklist:
            output_data.append(str(in_item))
    return output_data


def parse_jolokia_output(jolokia_server_url: str) -> Dict:
    invocation_url = f"{jolokia_server_url}jolokia/list"
    info(f"Analyzing MBeans with {invocation_url}")
    # var_name = f"{jolokia_server_url=}".partition("=")[0]
    resp = make_http_call(invocation_url)
    output_data = dict()
    temp_list = list()
    if resp.status_code == 200:
        contents = resp.json()
        for k, v in contents["value"].items():
            attr_name = list()
            mbean_name = k
            mbean_output = list()
            if re.fullmatch(instance_default_blacklist_pattern, str(mbean_name).lower()) is not None:
                info(f"{mbean_name} Jolokia MBean matched the global blacklist match and will be ignored.")
                continue
            for var_key, var_val in v.items():
                vars_name = [str(item) for item in str(var_key).split(",")]
                if "attr" in var_val:
                    attr_name = [str(attr_key) for attr_key, _ in var_val["attr"].items() if attr_key.lower() not in BASE_CONFIGS["IGNORED_ATTR_LIST"]]
                else:
                    attr_name = [".*"]
                mbean_output += mbean_common_format(mbean_name, vars_name, attr_name)
            temp_list += jolokia_output_whitelist_blacklist(mbean_output)
        temp_list.sort()
        for item in temp_list:
            output_data[item] = None
    return output_data


def parse_exporter_whitelist_blacklist_format(mbeans: List) -> List:
    output_data = list()
    mbeans.sort()
    for mbean_string in mbeans:
        mbean_name = ""
        vars_name = list()
        mbean_name = mbean_string.split(':', 1)[0]
        for item in str(mbean_string).split(":", 1)[1].split(","):
            var_out = str(item).split("=")
            if var_out[0] != "*":
                var_name = var_out[0]
                var_val = var_out[1] if var_out[1] != "*" else ".*"
                var_tag = "=".join([str(var_name), str(var_val)])
            else:
                var_tag = ".*"
            vars_name.append(str(var_tag))
        # vars_name = [str(item.split("=")[0]) for item in mbean_string.split(':', 1)[1].split(",")]
        # vars_name = [item if item != "*" else ".*" for item in vars_name]
        vars_name.sort()
        attr_name = ".*"
        mbean_output = mbean_common_format(mbean_name, vars_name, [str(attr_name)])
        output_data += mbean_output
    output_data.sort()
    if not output_data:
        return None
    return output_data


def parse_exporter_yaml(file_path: str) -> Tuple[List, List]:
    blacklisted_mbeans = dict()
    whitelisted_mbeans = dict()
    with open(file_path, 'r') as file:
        file_data = yaml.safe_load(file)
        blacklisted_mbeans = parse_exporter_whitelist_blacklist_format(file_data["blacklistObjectNames"] if "blacklistObjectNames" in file_data else [])
        whitelisted_mbeans = parse_exporter_whitelist_blacklist_format(file_data["whitelistObjectNames"] if "whitelistObjectNames" in file_data else [])
    return whitelisted_mbeans, blacklisted_mbeans


def parse_exported_mbean_format(help_line: str, type_line: str, metrics_lines: List, ):
    temp_extract = help_line.rpartition("(")[2].split(")", 1)[0]
    mbean_name = temp_extract.split("<", 1)[0]
    temp_others = str(temp_extract.split("<", 1)[1]).partition("><>")
    attr_name = [str(temp_others[2])]
    pattern_data = f".*,(.*)=\"{attr_name[0]}\""
    attr_matcher = re.search(pattern_data, metrics_lines[0])
    if attr_matcher:
        attr_group_name = str(attr_matcher.group(1))
        if attr_group_name is not None:
            for line in metrics_lines:
                inner_match = re.search(f".*,{attr_group_name}=\"(.+)\",", line)
                if inner_match:
                    attr_inner_name = str(inner_match.group(1))
                    if attr_inner_name is not None:
                        attr_name += [str(attr_inner_name)]
    # De-dupe all the attr-names
    attr_name = list(set(attr_name))
    vars_name = [str(f"{str(item.split('=')[0])}=.*") for item in temp_others[0].split(", ")]
    vars_name.sort()
    outstring = mbean_common_format(mbean_name, vars_name, attr_name)
    return outstring


def parse_exporter_output(url: str):
    total_list = list()
    output_data = OrderedDict()
    resp = make_http_call(url)
    if resp.status_code == 200:
        start_parsing, help_line, type_line, metrics_lines = False, None, None, None
        for line in resp.text.splitlines():
            # Check if its the HELP line
            if line.startswith("# HELP "):
                # Check if there's a bean in the HELP line
                if line.endswith(")"):
                    # If there is previous data in the export
                    if help_line is not None:
                        # We have to send the complete metrics block for parsing now as a new block seems to have started.
                        exported_mbean = parse_exported_mbean_format(help_line, type_line, metrics_lines)
                        total_list += exported_mbean
                    # Now reset everything and start all over again.
                    start_parsing = True
                    help_line = line
                    type_line: str = None
                    metrics_lines: List = list()
                # If no bean available to parse, skip the whole block as its of no use to us.
                else:
                    start_parsing = False
                    help_line = None
                    type_line: str = None
                    metrics_lines: List = list()
                continue
            elif line.startswith("# TYPE ") and start_parsing is True:
                type_line = line
                continue
            elif start_parsing is True:
                metrics_lines.append(str(line))
                continue
    total_list.sort()
    for item in total_list:
        output_data[item] = None
    return output_data


def write_csv(ignore_found_beans: bool = True):
    curr_date = datetime.now()
    str_date = curr_date.strftime("%Y_%m_%d_%H_%M")
    output_path = "/".join([BASE_CONFIGS["OUTPUT_CSV_PATH"], f"output_{str_date}.csv"])
    with open(output_path, "w") as csvfile:
        csvwriter = csv.writer(csvfile, dialect=csv.excel)
        fields = ['Component Name', 'Bean Status', "Bean Name", "Bean Attributes"]
        csvwriter.writerow(fields)
        for pod_name, pod_values in report.items():
            for bean_type, beans in pod_values.items():
                if ignore_found_beans is True and str(bean_type) == "found_beans":
                    continue
                csvwriter.writerows([[pod_name, bean_type, key, value] for key, value in beans.items()])


def generate_report():
    print(
        "{:<15} {:<15} {:<12} {:<12}".format(
            "Instance Name",
            "Instance Status",
            "Beans Found",
            "Beans Missed",
        )
    )
    for k, v in report.items():
        print(
            "{:<15} {:<15} {:<12} {:<12}".format(
                k,
                "Dont Know Yet",
                len(v["found_beans"]),
                len(v["missed_beans"])
            )
        )
    write_csv()


def add_bean_to_result(bean_to_add_to: dict, bean_name: str):
    bean_split = bean_name.rsplit(SPLITTER, 1)
    bean_identifier = bean_split[0]
    bean_attr = bean_split[1]
    checker = bean_to_add_to.get(bean_identifier)
    if checker is not None:
        checker += [str(bean_attr)]
    else:
        checker = [str(bean_attr)]
    bean_to_add_to[bean_identifier] = checker


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Command line arguments for controlling the application",
        add_help=True,
    )

    parser.add_argument(
        "--jmx-monitoring-stacks-base-fullpath",
        type=str,

        default=None,
        metavar="/Users/.../codebase/jmx-monitoring-stacks",
        help="Provide the full path of the jmx-monitoring-stacks repo here.",
    )

    args = parser.parse_args()

    if args.jmx_monitoring_stacks_base_fullpath is None:
        error("Cannot proceed forward if jmx-monitoring-stacks full path is not provided.")
        sys.exit(1)

    BASE_CONFIGS["BASE_EXPORTER_YAML_PATH"] = f"{args.jmx_monitoring_stacks_base_fullpath}/shared-assets/jmx-exporter"
    BASE_CONFIGS["OUTPUT_CSV_PATH"] = f"{args.jmx_monitoring_stacks_base_fullpath}/utils/testing/output"

    logging.basicConfig(format="%(levelname)s:\t\t%(message)s")
    report = dict()
    for instance_name, instance_config in CALL_MAPPINGS.items():
        # if instance_name not in ["KSQLDB"]:
        #     continue
        jmx_exporter_url = instance_config["EXPORTER"]
        jolokia_url = instance_config["JOLOKIA"]
        exporter_path = "/".join([BASE_CONFIGS["BASE_EXPORTER_YAML_PATH"], BASE_CONFIGS[instance_config["CONFIG"]]])

        info(f"Parsing exporter Profile to check Whitelists and Blacklists in file {exporter_path}")
        exporter_whitelist, exporter_blacklist = parse_exporter_yaml(exporter_path)

        instance_whitelist_pattern = "|".join(exporter_whitelist) if exporter_whitelist is not None else ""
        instance_blacklist_pattern = "|".join(exporter_blacklist) if exporter_blacklist is not None else ""
        default_blacklist: List = BASE_CONFIGS["IGNORED_BEAN_LIST"]
        instance_default_blacklist_pattern = "|".join(default_blacklist)

        jolokia_mbeans_output = parse_jolokia_output(jolokia_url)
        exporter_mbeans_output = parse_exporter_output(jmx_exporter_url)

        exporter_available_pattern = "|".join(exporter_mbeans_output.keys())

        found_mbeans = dict()
        missing_mbeans = dict()
        report[instance_name] = {"found_beans": found_mbeans, "missed_beans": missing_mbeans}
        for item in jolokia_mbeans_output.keys():
            match_result = re.match(exporter_available_pattern, item)
            if match_result is not None:
                add_bean_to_result(found_mbeans, str(item))
            else:
                add_bean_to_result(missing_mbeans, str(item))
                
    generate_report()
    info("Run Complete")
