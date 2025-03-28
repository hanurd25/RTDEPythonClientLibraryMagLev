#!/usr/bin/env python
# Copyright (c) 2020-2022, Universal Robots A/S,
# All rights reserved.
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * Neither the name of the Universal Robots A/S nor the names of its
#      contributors may be used to endorse or promote products derived
#      from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL UNIVERSAL ROBOTS A/S BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#
#
#
#
import argparse
import logging
import sys
import time
import csv
sys.path.append("..")
import rtde.rtde as rtde
import rtde.rtde_config as rtde_config

# parameters

#16.03.2025: 192.168.0.100
#
parser = argparse.ArgumentParser()
parser.add_argument("--host", default="192.168.0.100", help="Robot IP")
parser.add_argument("--port", type=int, default=30004, help="Port number")
parser.add_argument("--frequency", type=int, default=125, help="Sampling frequency")
parser.add_argument("--config", default="record_configuration.xml", help="Config file")
parser.add_argument("--output", default="../csv_data/jointData2.csv", help="Output file")
parser.add_argument("--verbose", action="store_true", help="Verbose output")
args = parser.parse_args()

if args.verbose:
    logging.basicConfig(level=logging.INFO)

conf = rtde_config.ConfigFile(args.config)
outputNames, outputTypes = conf.get_recipe("out")

con = rtde.RTDE(args.host, args.port)
con.connect()
con.get_controller_version()

if not con.send_output_setup(outputNames, outputTypes, frequency=args.frequency):
    logging.error("Unable to configure output")
    sys.exit()

if not con.send_start():
    logging.error("Unable to start synchronization")
    sys.exit()

with open(args.output, 'w', newline='') as csvfile:
    CSVWriter = csv.writer(csvfile)

    header = ["timestamp"] + [f"{name}_{i}" for name in outputNames for i in range(6)]
    CSVWriter.writerow(header)

    i = 1
    keepRunning = True
    while keepRunning:
        try:
            state = con.receive()
            if state is not None:
                timestamp = time.time()
                row = [timestamp]

                for name in outputNames:
                    vector_data = getattr(state, name)
                    row.extend(vector_data)

                CSVWriter.writerow(row)  # Write the row
                i += 1

        except rtde.RTDEException:
            con.disconnect()
            sys.exit()

con.send_pause()
con.disconnect()


