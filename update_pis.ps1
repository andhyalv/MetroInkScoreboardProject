$pis = @(
    "metro@192.168.8.111",
    "metro@192.168.8.198",
    "metro@192.168.8.200",
    "metro@192.168.8.143",
    "metro@192.168.8.180",
    "metro@192.168.8.230"
)

foreach ($pi in $pis) {
    Write-Host "Updating $pi..."
    ssh $pi "cd ~/MetroInkScoreboardProject && git pull"
}

Write-Host "All done!"