set -eux

# Update the v1 tag for GitHub Actions consumers
if [[ ${RH_DRY_RUN} != 'true' ]]; then
    git tag -f -a v1
    git push origin -f --tags
fi
