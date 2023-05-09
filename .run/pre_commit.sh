#!/usr/bin/env bash
#
# pre-commit.sh
# =============
#
#	Run format and lint checks against python files and fails
#   if any problems detected. This will stop git from committing.
#
function run_check {
	YELLOW='\033[1;33m'
	RED='\033[1;31m'
	GREEN='\033[1;32m'
	NC='\033[1;0m'
	printf "${GREEN}Running ${YELLOW}%9s${GREEN} against new python files ..... " $1
	$* $py_files >/dev/null 2>&1
	if [ $? -eq 0 ] ; then
		echo -e "${YELLOW} succeeded${NC}"
	else
		echo -e "${RED} 💥💥failed💥💥${NC}"
	fi
	((err++))
}
OIFS="$IFS"
IFS=$'\n'
err=0
py_files=$(git diff --cached --name-only --diff-filter=ACM |grep '.py$')
test -z "$py_files" && exit 0

echo -e "${YELLOW}Checking the following python files for problems:${NC}"
echo -e "$GREEN$(fold -w 76 -s <<<$py_files|sed 's/^/    /')${NC}"

run_check checktabs 
run_check black --check 
run_check isort --check-only 
run_check pylint -rn -sn 

if [ $err -gt 0 ] ; then
	exit 1
fi
