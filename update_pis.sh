#!/bin/bash
for pi in pi@192.168.8.111  pi@192.168.8.198 pi@192.168.8.200 pi@192.168.8.143  pi@192.168.8.180 pi@ 192.168.8.230; do
    echo "Updating $pi..."
    ssh $pi "cd ~/MetroInkScoreboardProject && git pull"
done
echo "All done!"