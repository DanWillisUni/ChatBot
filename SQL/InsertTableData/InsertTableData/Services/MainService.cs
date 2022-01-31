using InsertTableData.Configuration.Models;
using InsertTableData.Models;
using Microsoft.Extensions.Logging;
using System;
using System.Collections.Generic;
using System.Text;

namespace InsertTableData.Services
{
    public class MainService
    {
        private readonly ILogger<MainService> _logger;
        private readonly CSVReaderService<InputFile> _csvReader;
        private readonly CSVReaderService<Station> _stationCsvReader;
        private DB _db;
        public MainService(ILogger<MainService> logger, CSVReaderService<InputFile> csvReader, CSVReaderService<Station> stationCsvReader ,BasicConfiguration bc)
        {
            _logger = logger;
            _csvReader = csvReader;
            _stationCsvReader = stationCsvReader;
            _db = new DB(bc.connString);
        }
        public void root()
        {
            List<Station> stations = _stationCsvReader.readFromFile($"../../../DATA", $"stations");
            _db.insetStations(stations);
            _logger.LogInformation("Done stations");
            for (int year = 2017; year <= 2018; year++)
            {
                for (int month = 1; month <= 12; month++)
                {
                    List<InputFile> input = _csvReader.readFromFile($"../../../DATA/weymth_watlmn_2017_2018/{year}",$"WEYMTH_WATRLMN_OD_a51_{year}_{month}_{month}");
                    _db.insertData(input);
                    _logger.LogInformation($"Done {month}/{year}");
                }
            }
        }
    }
}
