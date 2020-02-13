#!/bin/bash
cd /home/opc/oci_metrics
source venv/bin/activate

export DATE=`date  '+%Y-%m-%d'`
#export DATE=`date '+%m/%d/%Y %I:%M %p'`
#export DATE=`TZ=CST6CDT date`

export APPDIR=$HOME/oci_metrics/oci_metrics/showoci
export REPORT_DIR=$HOME/oci_metrics/report_dir
export NEW_REPORT=${REPORT_DIR}/${DATE}
export CSV_DIR=${NEW_REPORT}/csv
#rm -rf ${REPORT_DIR}/*zip
#rm -rf ${NEW_REPORT}
mkdir -p ${NEW_REPORT}
mkdir -p ${CSV_DIR}

TENANCY=orasenatdpltoci01
#TENANCY=orasenatdecaretlhealth01
OUTPUT_FILE=${NEW_REPORT}/${TENANCY}_report.txt
JSON_FILE=${NEW_REPORT}/${TENANCY}_report.json
CSV_FILE=${CSV_DIR}/${TENANCY}

# Configure PSM CLI
psm setup --config-payload ${HOME}/.psm/conf/${TENANCY}.json

# Print Run Configurations
echo ""
echo "###################################################################################"
echo "# Start running oci_metrics on ${TENANCY} at `date`"
echo "# Output File = ${OUTPUT_FILE}"
echo "# CSV Directory = ${CSV_DIR}"
echo "###################################################################################"
echo ""
echo "Please Wait ..."

# python oci_metrics -t orasenatdpltoci01 -cpath "Development / Enterprise-Austin-Hub" -date $DATE -csv $CSV_FILE
python oci_metrics -t $TENANCY -rg us-ashburn-1 -cpath "Development / Enterprise-Austin-Hub" -date $DATE -csv $CSV_FILE

TENANCY=orasenatdecaretlhealth01
OUTPUT_FILE=${NEW_REPORT}/${TENANCY}_report.txt
JSON_FILE=${NEW_REPORT}/${TENANCY}_report.json
CSV_FILE=${CSV_DIR}/${TENANCY}

# Configure PSM CLI
psm setup --config-payload ${HOME}/.psm/conf/${TENANCY}.json

# Print Run Configurations
echo ""
echo "###################################################################################"
echo "# Start running oci_metrics on ${TENANCY} at `date`"
echo "# Output File = ${OUTPUT_FILE}"
echo "# CSV Directory = ${CSV_DIR}"
echo "###################################################################################"
echo ""
echo "Please Wait ..."

# python oci_metrics -t orasenatdpltoci01 -cpath "Development / Enterprise-Austin-Hub" -date $DATE -csv $CSV_FILE
python oci_metrics -t $TENANCY -rg us-ashburn-1 -cpath "Development / Enterprise-Austin-Hub" -date $DATE -csv $CSV_FILE