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
            return $"'{rid}','{tpl}','{pta}','{ptd}','{wta}','{wtp}','{wtd}','{arr_et}','{arr_wet}','{arr_atRemoved}','{pass_et}','{pass_wet}','{pass_atRemoved}','{dep_et}','{dep_wet}','{dep_atRemoved}','{arr_at}','{pass_at}','{dep_at}','{cr_code}','{lr_code}'";
        }
    }
}
