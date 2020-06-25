#!/bin/bash
# This script is used for run this project, it will automatically detect that
# whether today's learning task is completed, if completed, the project will not run,
# otherwise it will.
# NOTE: Please run this script in the project root path.

function help () {
    echo ""
    echo "Usage: "
    echo "  ./tools/run.sh"
    echo ""
    echo "NOTE: "
    echo "  Please run this script in the project root path."
    echo ""
}

CWD=$(pwd)
echo "CWD: ${CWD}"

if [[ ${CWD} != */Study ]]; then
    help
    exit
fi

latest_date_file_path="./study/log/latest_complete.date"

if [[ ! -f ${latest_complete_date_file_path} ]]; then
    python3 tools/run.py $@
else
    echo "Check latest complete date ..."

    current_date=`date '+%Y-%m-%d'`
    echo "current_date=${current_date}"

    latest_date=$(cat ${latest_date_file_path})
    echo "latest_date=${latest_date}"

    if test ${current_date} = ${latest_date}; then
        echo "Task all finished!"
    else 
        python3 tools/run.py $@
    fi
fi

echo "=================================================="
