﻿using InsertTableData.Models;
using InsertTableData.Services;
using InsertTableData;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using Serilog;
using System;
using System.Collections.Generic;
using System.Text;
using InsertTableData.Configuration.Models;

namespace InsertTableData
{
    public class Startup
    {
        private static ServiceCollection _serviceCollection;
        private static ServiceProvider _serviceProvider;
        private Microsoft.Extensions.Logging.ILogger logger;
        public void Start()
        {
            Log.Logger = new LoggerConfiguration()
                .Enrich.FromLogContext()
                .WriteTo.Console(restrictedToMinimumLevel : Serilog.Events.LogEventLevel.Information)
                .WriteTo.File("logs//" + DateTime.Today.ToString("yyyy") + "//" + DateTime.Today.ToString("MM") + "//" + DateTime.Today.ToString("dd") + "//ISD-" + DateTime.Now.ToString("HHmmss") + ".txt")
                .MinimumLevel.Debug()
                .CreateLogger();

            RegisterServices();

            logger = _serviceProvider.GetRequiredService<ILogger<Program>>();
            logger.LogInformation("Start");
            runMyStuff();
        }
        public void Stop()
        {
            logger.LogInformation("End");
            DisposeServices();
            System.Environment.Exit(0);
        }

        public void runMyStuff()
        {
            MainService ms = _serviceProvider.GetRequiredService<MainService>();
            ms.root();
            Stop();
        }

        private static void RegisterServices()
        {
            IConfiguration configuration = new ConfigurationBuilder()
                .AddJsonFile("Configuration/appsettings.json", optional: true, reloadOnChange: true)
                .Build();

            _serviceCollection = new ServiceCollection();

            var BasicSettings = new BasicConfiguration();
            configuration.Bind("BasicSettings", BasicSettings);
            _serviceCollection.AddSingleton(BasicSettings);

            _serviceCollection.AddSingleton<Program>();
            _serviceCollection.AddLogging(cfg => cfg.AddSerilog()).Configure<LoggerFilterOptions>(cfg => cfg.MinLevel = LogLevel.Debug);

            _serviceCollection.AddSingleton<MainService>();
            _serviceCollection.AddTransient<CSVReaderService<InputFile>>();
            _serviceCollection.AddTransient<CSVReaderService<Station>>();

            _serviceProvider = _serviceCollection.BuildServiceProvider(true);
        }
        private static void DisposeServices()
        {
            if (_serviceProvider == null)
            {
                return;
            }
            if (_serviceProvider is IDisposable)
            {
                ((IDisposable)_serviceProvider).Dispose();
            }
        }
    }
}
