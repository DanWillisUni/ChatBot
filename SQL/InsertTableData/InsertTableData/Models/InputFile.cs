using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Text;
using System.Text.Json;

namespace InsertTableData.Models
{
    public class InputFile
    {
        public string rid { get; set; }
        public string tpl { get; set; }
        public string pta { get; set; }
        public string ptd { get; set; }
        public string wta { get; set; }
        public string wtp { get; set; }
        public string wtd { get; set; }
        public string arr_et { get; set; }
        public string arr_wet { get; set; }
        public string arr_atRemoved { get; set; }
        public string pass_et { get; set; }
        public string pass_wet { get; set; }
        public string pass_atRemoved { get; set; }
        public string dep_et { get; set; }
        public string dep_wet { get; set; }
        public string dep_atRemoved { get; set; }
        public string arr_at { get; set; }
        public string pass_at { get; set; }
        public string dep_at { get; set; }
        public string cr_code { get; set; }
        public string lr_code { get; set; }



        public override string ToString()
        {
            return $"'{rid}','{tpl}',{getNulls(pta)},{getNulls(ptd)},{getNulls(wta)},{getNulls(wtp)},{getNulls(wtd)},{getNulls(arr_et)},{getNulls(arr_wet)},'{arr_atRemoved}',{getNulls(pass_et)},{getNulls(pass_wet)},'{pass_atRemoved}',{getNulls(dep_et)},{getNulls(dep_wet)},'{dep_atRemoved}',{getNulls(arr_at)},{getNulls(pass_at)},{getNulls(dep_at)},'{cr_code}','{lr_code}'";
        }
        private string getNulls(string input)
        {
            return input == "" || input == null ? "null" : "'" + input + "'";
        }
    }
}
