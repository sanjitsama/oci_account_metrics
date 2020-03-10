#!/bin/bash
cd /home/opc/oci_metrics
source venv/bin/activate

export DATE=`date  '+%Y-%m-%d'`
export APPDIR=$HOME/oci_metrics/oci_metrics/showoci
export REPORT_DIR=$HOME/oci_metrics/report_dir
export NEW_REPORT=${REPORT_DIR}/${DATE}
export CSV_DIR=${NEW_REPORT}/csv

rm -rf ${REPORT_DIR}/*
rm -rf ${NEW_REPORT}
mkdir -p ${NEW_REPORT}
mkdir -p ${CSV_DIR}

for filename in /home/opc/.oci/sessions/*; do

    ##################################
    # Run Report
    ##################################
    #TENANCY=${filename//+(*\/|.*)}
    TENANCY=$(basename "$filename")

    # Configure PSM CLI
    psm setup --config-payload ${HOME}/.psm/conf/${TENANCY}.json

    # Set Report Output File Paths
    OUTPUT_FILE=${NEW_REPORT}/${TENANCY}_report.txt
    JSON_FILE=${NEW_REPORT}/${TENANCY}_report.json
    CSV_FILE=${CSV_DIR}/${TENANCY}

    # Print Run Configurations
    echo ""
    echo "###################################################################################"
    echo "# Start running oci_metrics on ${TENANCY} at `date`"
    echo "# Output File = ${OUTPUT_FILE}"
    echo "# CSV Directory = ${CSV_DIR}"
    echo "###################################################################################"
    echo ""
    echo "Please Wait ..."

    # PRODUCTION Call (iterates through all tenancies, regions, compartments, etc.)
    # python oci_metrics -t ${TENANCY} -cpath "Development" -sjf $JSON_FILE -csv $CSV_FILE > $OUTPUT_FILE 2>&1
    
    # DEVELOPMENT Call
    python oci_metrics -t $TENANCY -date $DATE -csv $CSV_FILE
    
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
