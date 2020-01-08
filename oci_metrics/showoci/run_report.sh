#!/bin/bash
#############################################################################################################################
# Author - Adi Zohar, May 15th 2019
#
# Run daily report for crontab use
# Generates daily report including JSON file and latest CSV files
#
# Amend APPDIR, PYTHONPATH and REPORT_DIR
#
# Crontab set:
# 0 0 * * * timeout 6h /home/opc/showoci/run_daily_report.sh > /home/opc/showoci/run_daily_report_crontab_run.txt 2>&1
#############################################################################################################################
export DATE=`date '+%Y%m%d'`
export APPDIR=$HOME/oci_metrics/oci_metrics/showoci
export PYTHONPATH=$HOME/oci_metrics/venv
export REPORT_DIR=$HOME/oci_metrics/report_dir
export CSV_DIR=${REPORT_DIR}/csv
mkdir -p ${REPORT_DIR}
mkdir -p ${CSV_DIR}

##################################
# Run Report
##################################
OUTPUT_FILE=${REPORT_DIR}/${DATE}_report.txt
JSON_FILE=${REPORT_DIR}/${DATE}_report.json.txt
CSV_FILE=${CSV_DIR}/${DATE}_report

echo "###################################################################################"
echo "# Start running showoci at `date`"
echo "# Output File = $OUTPUT_FILE"
echo "# JSON   File = $JSON_FILE"
echo "###################################################################################"
echo "Please Wait ..."
python3 $APPDIR/showoci.py -ani -sjf $JSON_FILE -csv $CSV_FILE > $OUTPUT_FILE 2>&1

# Print Errors on screen
grep -i Error $OUTPUT_FILE

# Print Status
ERROR=""
WARNING=""
(( `grep -i Error $OUTPUT_FILE | wc -l` > 0 )) && ERROR=", with **** Errors ****"
(( `grep -i "Service Warning" $OUTPUT_FILE | wc -l` > 0 )) && WARNING=", with **** Warnings ****"

echo ""
echo "###################################################################################"
echo "# Finished at `date` $ERROR $WARNING "
echo "###################################################################################"

####################################################
# Cleanup - Gzip after 7 days, delete after 180
####################################################
/usr/bin/find ${REPORT_DIR} -name "*showoci_report*.txt" -mtime +7  -exec gzip '{}' \;
/usr/bin/find ${REPORT_DIR} -name "*showoci_report*.txt" -mtime +180 -exec rm -f '{}' \;
