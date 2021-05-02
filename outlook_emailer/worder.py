import pandas as pd
from win32com.client import Dispatch


wrd = Dispatch("Word.Application")
# doc = wrd.Documents.Add()
doc = wrd.Documents.Open(r'D:\projects\OutlookEmailer\doc_test.docx')
wrd.Visible = True
# определяю позицию куда вставить таблицу. Вставляю в конец документа
rng = doc.Content
rng.Collapse(Direction=0)

# добавляю таблицу в выбранное место
tbl = doc.Tables.Add(Range=rng, NumRows=2, NumColumns=11)

tbl.Borders.OutsideLineStyle = 1
tbl.Borders.InsideLineStyle = 1
tbl.Range.ParagraphFormat.Alignment = 1

tbl.Cell(1, 1).Merge(tbl.Cell(1, 11))

doc.SaveAs(r'D:\projects\OutlookEmailer\doc_test.docx')
doc.Close()
wrd.Quit()
