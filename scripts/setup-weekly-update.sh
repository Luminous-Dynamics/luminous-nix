#!/usr/bin/env bash
# Set up weekly model update cron job

echo "🕰️ Setting up weekly model update..."

# Create the cron job entry
CRON_JOB="0 2 * * 0 /srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity/scripts/weekly-model-update.sh >> /var/log/nix-trinity-update.log 2>&1"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "weekly-model-update.sh"; then
    echo "⚠️  Weekly update cron job already exists"
else
    # Add the cron job
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    echo "✅ Added weekly update cron job (Sundays at 2 AM)"
fi

# Create log directory if needed
sudo mkdir -p /var/log
sudo touch /var/log/nix-trinity-update.log
sudo chmod 666 /var/log/nix-trinity-update.log

echo "📝 Logs will be written to /var/log/nix-trinity-update.log"
echo ""
echo "To check the cron job:"
echo "  crontab -l"
echo ""
echo "To remove the cron job:"
echo "  crontab -l | grep -v weekly-model-update.sh | crontab -"
