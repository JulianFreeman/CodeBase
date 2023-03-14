function onEdit(e) {
  //格式：key: 表格名称，value: 自增列的列索引（从 1 开始）
  const allowedSheetNames = {
    "日志": 1,
  };
  //如果是删除值，会返回 undefined，我们忽略删除值的情况
  if (e.value !== undefined) {
    //当前编辑的表格
    const sheet = e.source.getActiveSheet();
    const sheetName = sheet.getName();
    //在允许自增的表格列表内
    if (sheetName in allowedSheetNames) {
      //自增列索引
      let idCol = allowedSheetNames[sheetName];
      //自增列标签
      let idColLabel = String.fromCharCode(64+idCol);
      //编辑单元格所在的行号
      let editedRow = e.range.getRow();
      //当编辑单元格所在的列号不是自增列时，如果编辑的是自增列我们忽略
      if (e.range.getColumn() !== idCol) {
        const rangeList = sheet.getRangeList([`${idColLabel}2:${idColLabel}`, `${idColLabel}${editedRow}`]).getRanges();
        //当编辑行的自增列单元格为空时我们自增，如果已经有值我们忽略
        if (rangeList[1].getValue().length === 0) {
          //返回结果形如 [[1], [2], [""], ...]，需要降维
          const ids = rangeList[0].getValues().flat();
          //过滤掉非数字的值，包括空字符串
          const validIds = ids.filter(elem => typeof elem === "number");
          //找最大值并加一
          let nextId = validIds.reduce((a, b) => Math.max(a, b), -Infinity) + 1;
          rangeList[1].setValue(nextId);
        }
      }
    }
  }
}
