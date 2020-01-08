#!/bin/bash
cd /home/opc/oci_metrics
source venv/bin/activate

export DATE=`date '+%Y%m%d'`
export APPDIR=$HOME/oci_metrics/oci_metrics/showoci
export REPORT_DIR=$HOME/oci_metrics/report_dir/${DATE}
export CSV_DIR=${REPORT_DIR}/csv
mkdir -p ${REPORT_DIR}
mkdir -p ${CSV_DIR}

for filename in /home/opc/.oci/sessions/*; do

    ##################################
    # Run Report
    ##################################
    #TENANCY=${filename//+(*\/|.*)}
    TENANCY=$(basename "$filename")
    OUTPUT_FILE=${REPORT_DIR}/${TENANCY}_report.txt
    JSON_FILE=${REPORT_DIR}/${TENANCY}_report.json
    CSV_FILE=${CSV_DIR}/${TENANCY}_report
    echo ""
    echo "###################################################################################"
    echo "# Start running oci_metrics on ${TENANCY} at `date`"
    echo "# Output File = $OUTPUT_FILE"
    echo "# JSON   File = $JSON_FILE"
    echo "###################################################################################"
    echo ""
    echo "Please Wait ..."

    python oci_metrics -t $TENANCY -date $DATE -csv $CSV_FILE > $OUTPUT_FILE
    # python oci_metrics -t ${TENANCY} -cpath "Development" -sjf $JSON_FILE -csv $CSV_FILE > $OUTPUT_FILE 2>&1
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
done

echo "###################################################################################"
echo "# Preparing report email and sending to key recipients ..."
echo "###################################################################################"

python ./oci_metrics/report.py -date $DATE
