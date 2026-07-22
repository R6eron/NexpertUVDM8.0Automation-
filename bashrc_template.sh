# Load UVDM aliases and onboarding
if [ -f "$HOME/.uvdm_aliases.sh" ]; then
  . "$HOME/.uvdm_aliases.sh"
fi

# Print onboarding on every new interactive terminal
case $- in
  *i*) uv_onboarding ;;
esac
