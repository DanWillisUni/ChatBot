using InsertTableData.Models;
using System;
using System.Collections.Generic;
using System.Data.SqlClient;
using System.Text;

namespace InsertTableData.Services
{
    public class DB
    {
        private readonly SqlConnection connection;
        public DB(string connString)
        {
            connection = new SqlConnection(connString);
        }
        public void insertData(List<InputFile> input)
        {
            connection.Open();
            foreach (InputFile s in input)
            {
                string query = "INSERT INTO dbo.nrch_livst_a51 (rid,tpl,pta,ptd,wta,wtp,wtd,arr_et,arr_wet,arr_atRemoved,pass_et,pass_wet,pass_atRemoved,dep_et,dep_wet,dep_atRemoved,arr_at,pass_at,dep_at,cr_code,lr_code) Values (" + s.ToString() +")";
                using (SqlCommand command = new SqlCommand(query, connection))
                {
                    command.ExecuteNonQuery();
                }
            }
            connection.Close();
        }
        public void insetStations(List<Station> input)
        {
            connection.Open();
            foreach (Station s in input)
            {
                string query = "INSERT [dbo].[Stations] ([name], [longname_name_alias], [alpha3], [tiploc], [column5]) Values (" + s.ToString() + ")";
                using (SqlCommand command = new SqlCommand(query, connection))
                {
                    command.ExecuteNonQuery();
                }
            }
            connection.Close();
        }

        public List<List<string>> RunCommand(string sqlCommand, int fieldNumber)
        {
            List<List<string>> r = new List<List<string>>();
            connection.Open();
            using (SqlCommand command = new SqlCommand(sqlCommand, connection))
            {
                using (SqlDataReader reader = command.ExecuteReader())
                {
                    while (reader.Read())
                    {
                        for (int i = 0; i < reader.FieldCount; i += fieldNumber)
                        {
                            List<string> line = new List<string>();
                            for (int o = 0; o < fieldNumber; o++)
                            {
                                line.Add(reader.GetValue(i + o).ToString());
                            }
                            r.Add(line);
                        }
                    }
                }
            }
            connection.Close();
            return r;
        }

    }
}
