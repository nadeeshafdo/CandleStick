<?php
// api.php

header('Content-Type: application/json');

// Check if the required parameters are set
if (!isset($_GET['fromCurrency']) || !isset($_GET['toCurrency'])) {
    echo json_encode(['error' => 'Invalid request parameters']);
    exit;
}

$fromCurrency = $_GET['fromCurrency'];
$toCurrency = $_GET['toCurrency'];

// Path to the Python executable
$pythonPath = 'python'; // Use 'python3' if that's the command on your system

// Path to the Python script
$pythonScriptPath = './fetch_data.py';

// Construct the command to execute the Python script
$command = escapeshellcmd("$pythonPath $pythonScriptPath $fromCurrency $toCurrency");

// Execute the command
exec($command, $output, $returnVar);

// Output the response as JSON
if ($returnVar === 0) {
    $jsonOutput = implode("\n", $output);
    echo $jsonOutput;
} else {
    echo json_encode(['error' => 'Failed to fetch data from API']);
}
?>
