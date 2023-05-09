# vim: set ft=bash ts=3 sw=3 expandtab:
# Create and update the virtualenv, synchronizing it to versions in poetry.lock

command_virtualenv() {
   # This shouldn't be neccessary ......
   # eval "$(pyenv init -)"
   # eval "$(pyenv virtualenv-init -)"

   # Create a new environment if neccessary
   pyenv virtualenvs|grep -q "^..${ENV_NAME} "
   if [ $? -eq 0 ] ; then
      highlight "Re-using existing pyenv ^$ENV_NAME^ ----------"
   else
      highlight "Creating virtualenv ^$ENV_NAME^ ----------"
      pyenv virtualenv $ENV_NAME
   fi

   # Set local environment
   pyenv local $ENV_NAME

	# Poetry sometimes gets confused without the next 2 exports and uses the global env
	# - I *hope* this is the solution
	export VIRTUAL_ENV=$(pyenv virtualenv-prefix)/envs/$ENV_NAME
	export PYENV_VIRTUAL_ENV=$(pyenv virtualenv-prefix)/envs/$ENV_NAME

   # Update pip and any other outdated packages
   pip list --outdated 2>/dev/null |sed -e '1,/--* -/ d' -e 's/ .*$//'|xargs -n1 pip3 install -U
   
   # Install any missing packages
   poetry install --sync --all-extras -v
   if [ $? != 0 ]; then
      echo "*** Failed to install the virtualenv"
      exit 1
   fi
   success "VirtualEnv installed"

}

